const acorn = require('acorn')
const fs = require('fs')
const walk = require("acorn-walk")
const jsdom = require("jsdom")
const { JSDOM } = jsdom

const buffer = fs.readFileSync('stages/stage2.js').toString();
const ast = acorn.parse(buffer);

const doc = (new JSDOM()).window.document;
const main = doc.createElement('main');

const state = {
    doc,
    main,
    scope: main,
    stack: [],
};

const escapeHTML = str => str.replace(/[&<>'"]/g, 
  tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag]));


walk.recursive(ast, state, {
    Program(node, s, c) {
        for(const subnode of node.body) {
            c(subnode, s);
        }
    },

    ForStatement(node, s, c) {
        c(node.init, s);

        let loopID = Math.floor(Math.random() * 2**32).toString(16);
        s.loopID = loopID;
        c(node.test, s);

        // loop body
        const el = this._createElement('i', s);
        s.stack.push(s.scope);
        s.scope = el;
        
        c(node.body, s);
        c(node.update, s);

        const jmp = this._createElement('a', s);
        jmp.href = `#${loopID}`;
        s.scope.appendChild(jmp);

        s.scope = s.stack.pop();
        s.scope.appendChild(el);
    },

    WhileStatement(node, s, c) {
        let loopID = Math.floor(Math.random() * 2**32).toString(16);
        s.loopID = loopID;
        c(node.test, s);

        // loop body
        const el = this._createElement('i', s);
        s.stack.push(s.scope);
        s.scope = el;
        
        c(node.body, s);

        const jmp = this._createElement('a', s);
        jmp.href = `#${loopID}`;
        s.scope.appendChild(jmp);

        s.scope = s.stack.pop();
        s.scope.appendChild(el);
    },

    IfStatement(node, s, c) {
        let el;
        c(node.test, s);

        // dup if else exists
        if(node.alternate) {
            el = this._createElement('dt', s);
            s.scope.appendChild(el);
        }

        // if true case
        el = this._createElement('i', s);
        s.stack.push(s.scope);
        s.scope = el;
        c(node.consequent, s);
        s.scope = s.stack.pop();
        s.scope.appendChild(el);

        // if false case
        if(node.alternate) {
            el = this._createElement('bdi', s);
            s.scope.appendChild(el);

            el = this._createElement('i', s);
            s.stack.push(s.scope);
            s.scope = el;
            c(node.alternate, s);
            s.scope = s.stack.pop();
            s.scope.appendChild(el);
        }
    },

    ReturnStatement(node, s, c) {
        c(node.argument, s);

        const el = this._createElement('rt', s);
        s.scope.appendChild(el);
    },

    FunctionDeclaration(node, s, c) {
        const func = this._createElement('dfn', s);
        func.id = node.id.name;

        const args = [...node.params].reverse();
        for(const arg of args) {
            const el = this._createElement('var', s);
            el.title = arg.name;
            func.appendChild(el);
        }

        s.stack.push(s.scope);
        s.scope = func;

        c(node.body, s);

        s.scope = s.stack.pop();
        s.scope.appendChild(func);
    },

    VariableDeclarator(node, s, c) {
        if(node.id.type !== 'Identifier') {
            throw `Declarator for ${node.id.type} not implemented`;
        }

        c(node.init, s);

        const el = this._createElement('var', s);
        el.title = node.id.name;
        s.scope.appendChild(el);
    },

    CallExpression(node, s, c) {
        let el, fname, is_top;

        if(s.scope.tagName == 'A') {
            throw 'Nested calls not allowed!';
        }
 
        // const prop = node.callee.property;
        switch(node.callee.type) {
            case 'Identifier':
                fname = node.callee.name;
                is_top = false;
            break;

            case 'MemberExpression':
                if(node.callee.computed) { // a[expr]()
                    throw `Computed calls not supported`;
                }

                c(node.callee.object, s);
                fname = node.callee.property.name;
                is_top = true;
            break;

            default:
                throw `${node.type} call not supported`;
        }

        el = this._createElement('a', s);
        el.href = `javascript:${fname}()`;
        if(is_top) {
            el.target = '_top';
        }
        
        s.stack.push(s.scope);
        s.scope = el;

        for(const arg of node.arguments) {
            c(arg, s);
        }
        
        s.scope = s.stack.pop();
        s.scope.appendChild(el);
    },

    AssignmentExpression(node, s, c) {
        switch(node.left.type) {
            case 'Identifier':
                this._processAssignmentOp(node, s, c);

                const el = this._createElement('var', s);
                el.title = node.left.name;
                s.scope.appendChild(el);
            break;
            
            case 'MemberExpression':
                c(node.left.object, s);

                if(node.left.computed) { // a[expr]
                    c(node.left.property, s);
                    this._processAssignmentOp(node, s, c);

                    const el = this._createElement('ins', s);
                    s.scope.appendChild(el);
                } else {
                    this._processAssignmentOp(node, s, c);

                    const el = this._createElement('samp', s);
                    el.innerHTML = node.left.property.name;
                    s.scope.appendChild(el);
                }
            
            break;
            
            default:
                throw `${node.left.type} lhs not supported in AssignmentExpression`;
        }
    },

    ObjectExpression(node, s, c) {
        let keys = [], vals = [];

        const tbl = s.doc.createElement('table');
        const hdr = s.doc.createElement('tr');
        const val = s.doc.createElement('tr');

        tbl.appendChild(hdr);
        tbl.appendChild(val);

        for(const prop of node.properties) {
            const th = s.doc.createElement('th');
            th.innerHTML = prop.key.value.toString();
            hdr.appendChild(th);

            const td = s.doc.createElement('td');
            s.stack.push(s.scope);
            s.scope = td;
            c(prop.value, s);
            s.scope = s.stack.pop();
            val.appendChild(td);
        }

        s.scope.appendChild(tbl);
    },

    ArrayExpression(node, s, c) {
        const arr = this._createElement('ol', s);
        
        for(const item of node.elements) {
            const el = this._createElement('li', s);
            
            s.stack.push(s.scope);
            s.scope = el;

            c(item, s);

            s.scope = s.stack.pop(s.scope);
            arr.appendChild(el);
        }

        s.scope.appendChild(arr);
    },

    MemberExpression(node, s, c) {
        let el;
        c(node.object, s);

        const prop = node.property;

        if(prop.type == 'Identifier' && node.computed == false) {
            el = this._createElement('rp', s);
            el.innerHTML = prop.name;
        } else {
            c(prop, s);
            el = this._createElement('address', s);
        }
        
        s.scope.appendChild(el);
    },

    BinaryExpression(node, s, c) {
        const optags = {
            '+': 'dd',
            '-': 'sub',
            '*': 'ul',
            '/': 'div',
            '==': 'em',
            '<': 'small',
            '>': 'big',

            '!=': 'em', // special case
        }
        
        if(!optags.hasOwnProperty(node.operator)) {
            throw `Operator ${node.operator} not implemented`;
        }

        c(node.left, s);
        c(node.right, s);
        const op = this._createElement(optags[node.operator], s);
        s.scope.appendChild(op);

        // special case
        if(node.operator == '!=') {
            const not = this._createElement('bdi', s);
            s.scope.appendChild(not);
        }
    },

    LogicalExpression(node, s, c) {
        const optags = {
            '&&': 'b',
            '||': 'bdo'
        }
        
        if(!optags.hasOwnProperty(node.operator)) {
            throw `Operator ${node.operator} not implemented`;
        }

        c(node.left, s);
        c(node.right, s);
        const op = this._createElement(optags[node.operator], s);
        s.scope.appendChild(op);
    },

    UnaryExpression(node, s, c) {
        switch(node.operator) {
            case '!':
                c(node.argument, s);
                const op = this._createElement('bdi', s);
                s.scope.appendChild(op);
                break;

            case '-':
                if(node.argument.type == 'Literal') {
                    node.argument.value = -1 * node.argument.value;
                } else {
                    throw `Operator ${node.operator} not implemented for non-literals`;
                }

                c(node.argument, s);
                break;

            default:
                throw `Operator ${node.operator} not implemented`;
        }
        

    },

    Literal(node, s, c) {
        let el;
        const type = typeof node.value;
        switch(type) {
            case 'boolean':
                el = this._createElement('cite', s);
                el.innerHTML = node.value.toString();
                s.scope.appendChild(el);

                break;
            case 'number':
                el = this._createElement('data', s);
                el.value = node.value;    
                break;

            case 'string':
                el = this._createElement('s', s);

                // JSDOM doesn't support innerText,
                // so we have to reimplement it here
                el.innerHTML = escapeHTML(node.value);
                break;
            
            default:
                throw `Literal ${type} not implemented`
        }

        s.scope.appendChild(el);
    },

    Identifier(node, s, c) {
        const el = this._createElement('cite', s);
        el.innerHTML = node.name;
        s.scope.appendChild(el);
    },

    _createElement(name, s) {
        const el = s.doc.createElement(name);
        if(s.loopID) {
            el.id = s.loopID;
            s.loopID = null;
        }
        return el;
    },

    _processAssignmentOp(node, s, c) {
        const optags = {
            '+=': 'dd',
            '-=': 'sub',
            '*=': 'ul',
            's': 'div',
            '=': null,
        }

        if(!optags.hasOwnProperty(node.operator)) {
            throw `Operator ${node.operator} not implemented`;
        }

        if(node.operator == '=') {
            c(node.right, s);
        } else {
            c(node.left, s);
            c(node.right, s);
            const op = this._createElement(optags[node.operator], s);
            s.scope.appendChild(op);
        }
    }
})

const body = fs.readFileSync('template.html').toString().replace('%MAIN%', main.outerHTML);
fs.writeFileSync('code.html', body);

window.g = globalThis;
g.level = 1;

function addParagraph(child) {
    const el = document.createElement('p');
    if(child) {
        el.appendChild(child);
    }
    document.body.appendChild(el);
    return el;
}

function pow(a, b) {
    if(!pow.memo) {
        pow.memo = {};
    }
    var k = a + '_' + b;
    if(pow.memo[k]) {
        return pow.memo[k];
    }

    var result = 1;
    for(var i = 0; i < b; i = i+1) {
        result *= a;
    }

    pow.memo[k] = result;
    return result;
}

function xor(a, b) {
    var result = 0;

    for(var i = 0; i < 52; i = i+1) {
        var p = pow(2, 51-i);
        var ba = a > p - 1;
        var bb = b > p - 1;

        a = a - p * ba;
        b = b - p * bb;
        
        if(ba != bb) {
            result += p;
        }
    }
    return result;
}

function mod(a, b) {
    while(1) {
        if(a < b) {
            return a;
        }
        a -= b;
    }
}

function rc4(key, str) {
	var s = [];
    var j = 0;
    var x = '';
    var res = '';

	for (var i = 0; i < 256; i = i+1) {
		s[i] = i;
	}
	for (i = 0; i < 256; i = i+1) {
        var ki = mod(i, key.length);
        var kc = key.charCodeAt(ki);
		j = mod(j + s[i] + kc, 256);
		x = s[i];
		s[i] = s[j];
		s[j] = x;
	}
	i = 0;
	j = 0;    
    
	for (var y = 0; y < str.length; y = y+2) {
		i = mod(i + 1, 256);
		j = mod(j + s[i], 256);
		x = s[i];
		s[i] = s[j];
		s[j] = x;

        var cc = str.codePointAt(y) - 0x1f300;
        var si = mod(s[i] + s[j], 256);
        var xc = xor(cc, s[si]);

		res += String.fromCharCode(xc);
	}
	return res;
}

function checkPassword(el) {
    var elem = document.getElementById('password');
    var pval = elem.value;

    if(g.level == 1) {  
        var p = [];
        for(var i = 0; i < pval.length; i = i+1) {
            var c = pval.charCodeAt(i);
            p.push(c);
        }
            
        if(
            (105*p[xor(205,203)]+5668)+(p[xor(250-148,106)]+64)+xor(p[0],p[11])+(p[xor(26-12,1)])==13559&&
            (99*p[xor(508-481,25)]+3213)+(p[xor(649+179,826)])+xor(18*p[4],p[11])+(199*p[xor(91,623-540)]-6269)+xor(p[15],57*p[14]-1058)==24051&&
            (p[xor(278,166+114)])+(243*p[xor(456,449)]+5468)+(126*p[xor(22,28)]+8530)+(p[xor(393,530-132)])+xor(62*p[6]-4199,25*p[15]+837)+xor(53*p[12]-3060,p[5])+(p[xor(909,905)])==59369&&
            (p[xor(677,871-195)])+(p[xor(544,553)])+(186*p[xor(543,540)])+(p[xor(97,107)]+10)+xor(61*p[4]+3899,p[2])+(31*p[xor(703-375,334)]+1802)+xor(63*p[14]+3698,159*p[12]-1918)==25709&&
            (p[xor(986,979)])+xor(81*p[5],p[7]+112)+xor(197*p[3]+2873,148*p[2])+xor(240*p[12]+3406,p[14])==30641&&
            (p[xor(852+393,1246)]+58)+(p[xor(97,995-892)])+(p[xor(1425,754+675)])+(p[xor(398-327,75)]-16)+(p[xor(831,829)])+(227*p[xor(157,427-273)]-3709)==22153&&
            xor(p[15]-22,p[11])+xor(102*p[9]+11843,147*p[5]-9577)+(154*p[xor(990,774+204)])==30992&&
            (p[xor(599,588+11)])+(216*p[xor(343,797-458)]-3127)+xor(p[3]-25,p[7]+74)+xor(p[1]+64,p[2])+xor(p[11]+65,109*p[15])==18925&&
            xor(175*p[7]-346,p[14])+(33*p[xor(774,779)])+(p[xor(429+410,834)]+85)+(p[xor(297,591-303)])+xor(p[8],121*p[6]+7013)+xor(p[12],p[0]+0)==37284&&
            (p[xor(316,308)]-28)+xor(p[7],228*p[5])+xor(p[0]-24,p[14]-69)+xor(p[13]+30,243*p[6]+13372)==55341&&
            (172*p[xor(269-168,97)])+(143*p[xor(398,290+97)]-5399)+(120*p[xor(436,767-334)]-8863)+xor(221*p[1]-14162,p[9])+(p[xor(631,625)]+53)+(237*p[xor(55,37+26)]-625)==35798&&
            (140*p[xor(643,649)]-902)+(52*p[xor(651,644)]+2288)+(248*p[xor(139,270-131)]-2790)+(p[xor(617+611,1216)])+(p[xor(0,5)]-60)+(241*p[xor(696,809-110)])+(p[xor(907+481,1377)]+36)+xor(14*p[2],p[11]-30)==61301&&
            xor(p[12],54*p[13])+xor(4*p[10],233*p[4]-12942)+(17*p[xor(768,430+343)]-128)==8458&&
            (p[xor(854,859)]-5)+(p[xor(437,321+113)])+(p[xor(537+481,1011)])+(236*p[xor(217,375-166)]+7285)+xor(p[6]-35,29*p[2]+718)+xor(84*p[0],82*p[12])==39804&&
            (163*p[xor(707-407,297)]-12301)+(44*p[xor(193,503-306)]-812)+xor(p[13]-0,33*p[1])+xor(81*p[14],p[6])+(18*p[xor(1682,900+785)])==19267&&
            xor(17*p[11]+179,37*p[8])+xor(p[6]+59,p[10]+96)+(p[xor(457,309+149)])+xor(p[12],p[5]+64)+(p[xor(1109,740+372)]-9)==4463
        ) {

            var decrypted = rc4(pval, globalThis.d);
            decrypted = JSON.parse(decrypted);
            
            msg.innerText = 'Level 1 flag: ' + decrypted.flag;
            msg.style.color = '';
            elem.placeholder = 'Enter level 2 password';
            g.level += 1;    
        } else {
            msg.innerText = 'nah';
            msg.style.color = 'red';
        }
        elem.value = '';
    } else {

        var d = [46148559965, 56204584959, 12541431273, 16125790836, 68046076398, 19863008166, 51802968263, 67980034667, 44866526730];
        alert(d);
    }
}

const input = document.createElement('input');
input.id = 'password';
input.type = 'text';

input.placeholder = 'Enter password';
input.value = 'pWnBHiIp6vfoK6Y8';
addParagraph(input);

const btn = document.createElement('button');
btn.innerText = 'Check';
btn.addEventListener('click', checkPassword);
addParagraph(btn);
addParagraph(false).id = 'msg';

g.d = '🏋🎡🎈🍸🏣🏰🏤🌃🎹🍭🎧🍒🍒🌲🍖🍅🎔🏿🍥🍩🏉🌟🎦🍞🎐🌾🏉🍂🌫🍠🏯🏚🎒🎝🌕🏭🌳🍉🎫🍰🎅🏮🍉🏣🍭🏋🍈🏷🎜🏯🍄🌞🏕🍵🎃🎞🍎🎗🍕🌧🎘🎆🍁🏊🌑🏨🍶🍖🌍🎁🌫🌒🌖🏞🏂🎵🌷🏃🏁🌔🌄🌎🎒🏀🎶🎧🎬🌤🍧🎫🍳🍘🏨🍸';

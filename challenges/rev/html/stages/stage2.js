
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

// STAGE2 STUFF

var d = [46148559965, 56204584959, 12541431273, 16125790836, 68046076398, 19863008166, 51802968263, 67980034667, 44866526730];
var kk = [60, 240, 59, 98, 14, 230, 15, 23, 5, 174, 70, 3, 57, 55, 70, 204, 39, 21, 63, 112, 30, 221, 250, 60, 118];

function or(a, b) {
    var result = 0;

    for(var i = 0; i < 52; i = i+1) {
        var p = pow(2, 51-i);
        var ba = a > p - 1;
        var bb = b > p - 1;

        a = a - p * ba;
        b = b - p * bb;
        
        if(ba || bb) {
            result += p;
        }
    }
    return result;
}


function shr(a, b) {
    var result = 0;
    for(var i = 0; i < 52 - b; i = i+1) {
        var p = pow(2, 51-i);
        var bt = a > p - 1;
        if(bt) {
            result += pow(2, 51-i-b);
        }
        a = a - p * bt;
    }
    return result;
}

function shl(a, b) {
    return a * pow(2, b);
}

function and(a, b) {
    var result = 0;

    for(var i = 0; i < 52; i = i+1) {
        var p = pow(2, 51-i);
        var ba = a > p - 1;
        var bb = b > p - 1;

        a = a - p * ba;
        b = b - p * bb;
        
        if(ba && bb) {
            result += p;
        }
    }
    return result;
}

function extract(hi, lo, x) {
    var shifted =  shr(x, lo);
    var p = pow(2, (hi - lo) + 1) - 1;
    return and(shifted, p);
}

function combine(a, d) {
    var result = [];
    var k = 0;
    for(var i = 0; i < d.length; i = i+1) {
        var r = 0;
        for(var j = 0; j < 36; j = j+4) {
            var v = extract(j + 4 - 1, j, d[i]);
            if(!v || v > 9) {
                v = a[k];
                k += 1;
            }

            var sh = shl(v, j);
            r = or(r, sh);
        }
        result.push(r);
    }
    return result;
}


function verify(arr) {
    for(var i = 0; i < arr.length; i+=1) {
        var r = 0;
        for(var j = 0; j < arr.length * 4; j += 4) {
            var v = extract(j + 4 - 1, j, arr[i]);
            var b = shl(1, v - 1);
            r = or(r, b);
        }
        if(r != 511) {
            return false;
        }
    }

    for(var i = 0; i < arr.length * 4; i += 4) {
        var r = 0 ;
        for(var j = 0; j < arr.length; j+=1) {
            var v = extract(i + 4 - 1, i, arr[j]);
            var b = shl(1, v - 1);
            r = or(r, b);
        }
        if(r != 511) {
            return false;
        }
    }

    var rlop = [[0, 2], [3, 5], [6, 8]];
    for(var a = 0; a < rlop.length; a += 1) {
        var r1 = rlop[a];

        for(var b = 0; b < rlop.length; b += 1) {
            var r2 = rlop[b];

            var r = 0;
            for(var i = r1[0]; i < r1[1] + 1; i += 1) {
                for(var j = r2[0] * 4; j < (r2[1] + 1) * 4; j+= 4) {
                    var v = extract(j + 4 - 1, j, arr[i]);
                    var z = shl(1, v - 1);
                    r = or(r, z);
                }
            }

            if(r != 511) {
                return false;
            }
        }

    }
    return true;
}

function s2a(s, k) {
    var r = [];
    for(var i = 0; i < s.length; i+=1) {
        var c = s.charCodeAt(i);
        var b = xor(c, k[i]);

        var m = and(b, 0xf);
        var l = shr(b, 4);
        r.push(m);
        r.push(l);
    }
    return r;
}

var a = s2a('TaHPKonTP6PKZeTI3FWefIiTc', kk);

var comb = combine(a, d);
var r = verify(comb);

alert(r);

from cinspector.interfaces import CCode
from cinspector.analysis import CFG, BaseCFG

SRC1 = """
void a(int p) {
    int b = 1;
    while (b < 10) {
        b++;
        if (b == 8) {
            goto label1;
        }
    }
    for (int i = 0; i < 10; i++) {
        b--;
    }
    return;
label1:
    printf("6");
    return;
}
"""


def test_A(capsys):
    cc = CCode(SRC1)
    func = cc.get_by_type_name('function_definition')[0]
    cfg = CFG(func)
    for path in cfg.execution_path():
        print('=' * 10)
        for p in path:
            print(p)
    captured = capsys.readouterr()
    assert captured.out == """==========
int b = 1;
[while][Y]((b < 10))
b++;
[if][Y](b == 8)
goto label1;
printf("6");
return;
==========
int b = 1;
[while][Y]((b < 10))
b++;
[if][N](b == 8)
[for][Y](int i = 0; i < 10; i++)
b--;
return;
==========
int b = 1;
[while][Y]((b < 10))
b++;
[if][N](b == 8)
[for][N](int i = 0; i < 10; i++)
return;
==========
int b = 1;
[while][N]((b < 10))
[for][Y](int i = 0; i < 10; i++)
b--;
return;
==========
int b = 1;
[while][N]((b < 10))
[for][N](int i = 0; i < 10; i++)
return;
"""


SRC2 = """
int b = 1;
do {
    if (b == 1) {
        c(0);
    } else if (b == 2) {
        c(2);
    } else {
        c(3);
    }
} while (b < 10);

if (b == 1) {
    printf("6");
}
"""


def test_B(capsys):
    cc = CCode(SRC2)
    stmts = cc.node.children
    cfg = BaseCFG(stmts)
    for path in cfg.execution_path():
        print('*' * 10)
        for p in path:
            print(p)
    captured = capsys.readouterr()
    assert captured.out == """**********
int b = 1;
[if][Y](b == 1)
c(0);
[do-while][]((b < 10))
[if][Y](b == 1)
printf("6");
**********
int b = 1;
[if][Y](b == 1)
c(0);
[do-while][]((b < 10))
[if][N](b == 1)
**********
int b = 1;
[if][N](b == 1)
[if][Y](b == 2)
c(2);
[do-while][]((b < 10))
[if][Y](b == 1)
printf("6");
**********
int b = 1;
[if][N](b == 1)
[if][Y](b == 2)
c(2);
[do-while][]((b < 10))
[if][N](b == 1)
**********
int b = 1;
[if][N](b == 1)
[if][N](b == 2)
c(3);
[do-while][]((b < 10))
[if][Y](b == 1)
printf("6");
**********
int b = 1;
[if][N](b == 1)
[if][N](b == 2)
c(3);
[do-while][]((b < 10))
[if][N](b == 1)
"""

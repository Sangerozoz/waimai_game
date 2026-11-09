"""Load only completed read-only input/geometry prefix, without writing or running search."""
import ast
from pathlib import Path
from types import SimpleNamespace

def load():
    p=Path(__file__).with_name('plan_compound.py')
    prefix=p.read_text().split('single=[];trials=[];bySource={};inventory=[]')[0]
    tree=ast.parse(prefix)
    tree.body=[v for v in tree.body if not (isinstance(v,ast.Expr) and isinstance(v.value,ast.Call) and isinstance(v.value.func,ast.Name) and v.value.func.id=='write')]
    ns={'__file__':str(p)}
    exec(compile(tree,str(p)+':read-only-prefix','exec'),ns)
    return SimpleNamespace(**ns)

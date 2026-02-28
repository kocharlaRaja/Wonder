from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
import ast
import operator
import math

from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define allowed operators for safe evaluation
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Define allowed functions for safe evaluation
ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "fabs": math.fabs,
    "ceil": math.ceil,
    "floor": math.floor,
    "round": round,
}

class Evaluator(ast.NodeVisitor):
    def visit_Num(self, node):
        return node.n

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return ALLOWED_OPERATORS[type(node.op)](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        return ALLOWED_OPERATORS[type(node.op)](operand)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ALLOWED_FUNCTIONS:
                args = [self.visit(arg) for arg in node.args]
                return ALLOWED_FUNCTIONS[func_name](*args)
        raise TypeError(f"Unsupported function call: {ast.dump(node)}")

    def visit_Name(self, node):
        if node.id in ["pi", "e"]: # Allow constants
            return getattr(math, node.id)
        raise TypeError(f"Unsupported name: {node.id}")

    def generic_visit(self, node):
        raise TypeError(f"Unsupported operation: {ast.dump(node)}")

def safe_eval(expression):
    try:
        node = ast.parse(expression, mode='eval')
        return Evaluator().visit(node.body)
    except (SyntaxError, TypeError, ZeroDivisionError, OverflowError) as e:
        raise ValueError(f"Invalid expression or operation: {e}")

@app.post("/calculate", response_model=schemas.CalculationResponse)
def calculate_expression(
    calculation: schemas.CalculationCreate, db: Session = Depends(get_db)
):
    try:
        # Replace 'x' with '*' for multiplication if it's a common calculator input
        # This is a simple heuristic and might need more robust parsing for complex expressions
        processed_expression = calculation.expression.replace('x', '*')
        result_value = safe_eval(processed_expression)
        result_str = str(result_value)

        db_calculation = models.Calculation(
            expression=calculation.expression, result=result_str
        )
        db.add(db_calculation)
        db.commit()
        db.refresh(db_calculation)
        return db_calculation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/history", response_model=list[schemas.CalculationResponse])
def get_calculation_history(db: Session = Depends(get_db)):
    history = db.query(models.Calculation).order_by(models.Calculation.timestamp.desc()).all()
    return history

from fastapi import HTTPException
from fastapi.responses import JSONResponse


def ThrowException(status_code: int, detail: str, headers=None):
    if headers is None:
        raise HTTPException(status_code=status_code, detail=detail)
    else:
        raise HTTPException(status_code=status_code, detail=detail, headers={"X-Header-Error": headers})


def Response(content: object, status_code: int, headers: str = None):
    if headers is None:
        return JSONResponse(content=content, status_code=status_code)
    else:
        return JSONResponse(content=content, status_code=status_code, headers={"X-Header-Info": headers})

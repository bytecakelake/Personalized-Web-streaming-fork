# =============================================================================
# SPDX 가이드: https://reuse.software/spec/
# SPDX-FileCopyrightText: © 2024 bytecakelake <creator@bytecake.dev>
# SPDX-License-Identifier: AGPL-3.0 license
# =============================================================================
# ++ 목차 ++
# 
# =============================================================================
# ++ 할일 목록 ++
# TODO: 버전 1의 모든 엔드포인트 기획 및 구성을 완료하세요.
# TODO: 아직 미쳐 작성하지 못한 주석들을 작성하세요.
# TODO: 목차를 완성하세요.
# TODO: sqlite3 데이터베이스의 데이터 아키텍처를 설계한 후, 할일 목록을 업데이트하세요.
# TODO: 요청 및 응답 모델을 재설계하세요.
# =============================================================================
# TITLE: 모듈 실행 방지
# DESCRIPTION: 모듈을 커맨드 라인에서 실행하는것을 방지합니다.
if __name__ == "__main__": raise RuntimeError("이 스크립트는 직접 실행할 수 없습니다.")
# =============================================================================
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import ORJSONResponse, FileResponse
from sqlmodel import create_engine, Session, select, SQLModel
from pathlib import Path
import dbmodel as DA
from sqlalchemy.exc import NoResultFound, IntegrityError
# =============================================================================
# TITLE: 버전별 API 라우터 정의

apis: dict[str, APIRouter] = { # 버전별 API 라우터 객체 [버전, API 라우터 인스턴스]
    "v1": APIRouter(
        default_response_class=ORJSONResponse,
    ),
}
# =============================================================================
# db 조작 및 관리 클래스
class Database:
    path: Path = Path.home() / ".pws-restapi-server"
    name: str = "main_v1.db"
    def __init__(self):
        self.engine = self.create_engine()
    def new_session(self):
        return Session(self.engine)
    def create_engine(self):
        path = self.path / self.name
        if not path.exists():
            path.mkdir()
        return create_engine(f"sqlite:///{path}")

db = Database()
# =============================================================================
# TITLE: 응답 모델 정의
# DESCRIPTION: API 엔드포인트에서 반환하는 응답 모델을 정의합니다.
# NOTE: 임시로 정의된 응답 모델입니다. 
# TODO: 데이터 아키텍처 설계 후 수정이 필요합니다.
class ArtistSimpleInfo(BaseModel):
    profile_url: str
    name: str
#
class AlbumSimpleInfo(BaseModel):
    id: int
    title: str
    cover_url: str
#
class MusicGeneralInfo(BaseModel):
    id: int
    title: str
    hls_endpoint: str
    artist: ArtistSimpleInfo
    album: AlbumSimpleInfo
# =============================================================================
# TITLE: 엔드포인트 정의
#
# NOTE: 무분별한 크롤링을 방지하기 위해 GET 메서드를 지양하고 POST 메서드를 권장합니다.
#

## =============================================================================
## TITLE: 사용자 맞춤형 추천
## DESCRIPTION: 사용자의 선호도에 따라 추천 서비스을 제공합니다.
## NOTE: 추후 버전에서 사용자 맞춤형 추천 서비스를 제공할 예정입니다.
# >> ignore-endpoints (/recommended/*/**) {

## ENDPOINT: /recommended/{id}/music
## DESCRIPTION: 사용자에게 추천할 음악을 제공합니다.

## ENDPOINT: /recommended/{id}/artist
## DESCRIPTION: 사용자에게 추천할 아티스트를 제공합니다.

## ENDPOINT: /recommended/{id}/album
## DESCRIPTION: 사용자에게 추천할 앨범을 제공합니다.

## } ignore-endpoints <<
## =============================================================================
## TITLE: 쿼리 기능
## DESCRIPTION: 인덱스 검색 및 오브젝트 목록 조회 기능을 제공합니다.
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/query/serach", response_model=None, tags=["query", "search", "read"])
async def query_search() -> dict[str, object]:
    """
    ## READ: 데이터베이스에서 검색어에 맞는 오브젝트 목록을 조회합니다.
    
    ### Request
    - `body`
        - `target-types`: 검색 대상, 기본값은 `all`입니다.
        - `target-keyword`: 검색어
        - `batch-size`: 한 번에 가져올 오브젝트의 개수, 기본값은 `10`입니다.
        - `offset`: 가져올 오브젝트의 시작 위치, 기본값은 `0`입니다.
        
    ### Response
    
    - `status code` 상태 설명
        - `200`: object[]
        - `201`: HTTPException{"검색 결과가 없습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    pass
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
## =============================================================================
## TITLE: 엘범 기능
## DESCRIPTION: (공식/사용자 커스텀)엘범 오브젝트의 생성, 조회, 수정, 삭제 기능을 제공합니다.
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////

class AlbumDefineBody(BaseModel):
    released_at: int | None = None
    title: str | None = None
    length: int | None = None
    artist_name: str | None = None
    cover_block_key: str | None = None

@apis["v1"].post("/album/{id}/define", status_code=201, tags=["album", "define", "create"])
async def album_define_query(id: str, body: AlbumDefineBody):
    """
    ## CREATE: 앨범 오브젝트를 생성합니다.
    
    ### Request
    - `path parameter`
        - `id`: 앨범 ID
    
    ### Response
    
    - `status code` 상태 설명
        - `201`: Message{"요청하신 앨범을 생성했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `410`: HTTPException{"요청하신 앨범을 생성할 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    with db.new_session() as session:
        try:
            session.add(DA.AlbumTable(album_id=id, released_at=body.released_at, title=body.title, artist_name=body.artist_name, cover_block_key=body.cover_block_key))
            session.commit()
        except IntegrityError:
            raise HTTPException(status_code=410, detail="요청하신 앨범은 이미 존재하는 앨범입니다.")
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/album/{id}/info", tags=["album", "info", "read"])
async def album_info_query(id: str):
    """
    ## READ: 데이터베이스에서 기본적인 앨범 정보를 조회합니다.
    
    ### Request
    - `path parameter`
        - `id`: 앨범 ID
    
    ### Response
    
    - `status code` 상태 설명
        - `200`: AlbumSimpleInfo
        - `404`: HTTPException{"요청하신 앨범을 찾을 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    with db.new_session() as session:
        try:
            album = session.exec(select(DA.AlbumTable).where(DA.AlbumTable.album_id == id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="요청하신 앨범이 존재하지 않습니다.")
        return album
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/album/{id}/modify", response_model=None, tags=["album", "modify", "update"])
async def album_modify_query(id: str, body: AlbumDefineBody):
    """
    ## UPDATE: 앨범 오브젝트를 수정합니다.
    
    ### Request
    - `path parameter`
        - `id`: 앨범 ID
    - `body`
        - `id`: 변경될 앨범 ID, 선택사항입니다.
        - `title`: 변경될 앨범 제목, 선택사항입니다.
        - `cover_url`: 변경될 앨범 커버 URL, 선택사항입니다.
        
    ### Response
    
    - `status code` 상태 설명
        - `200`: Message{"요청하신 앨범을 수정했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `403`: HTTPException{"요청하신 앨범을 수정할 권한이 없습니다."}
        - `404`: HTTPException{"등록된 앨범을 찾을 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
        
    """
    with db.new_session() as session:
        try:
            album = session.exec(select(DA.AlbumTable).where(DA.AlbumTable.album_id == id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="요청하신 앨범이 존재하지 않습니다.")
        if body.released_at != None:
            album.released_at = body.released_at
        if body.title != None:
            album.title = body.title
        if body.length != None:
            album.length = body.length
        if body.artist_name != None:
            album.artist_name = body.artist_name
        if body.cover_block_key != None:
            album.cover_block_key = body.cover_block_key
        session.add(album)
        session.commit()
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/album/{id}/remove", tags=["album", "remove", "delete"])
async def album_remove_query(id: str, body: AlbumDefineBody):
    """
    ## DELETE: 앨범 오브젝트를 삭제합니다.
    
    ### Request
    - `path parameter`
        - `id`: 앨범 ID
    
    ### Response
    
    - `status code` 상태 설명
        - `201`: Message{"요청하신 앨범을 삭제했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `403`: HTTPException{"요청하신 앨범을 삭제할 권한이 없습니다."}
        - `404`: HTTPException{"요청하신 앨범을 찾을 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
        
    """
    with db.new_session() as session:
        try:
            album = session.exec(select(DA.AlbumTable).where(DA.AlbumTable.album_id == id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="요청하신 앨범이 존재하지 않습니다.")
        session.delete(album)
        session.commit()
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
## =============================================================================
## TITLE: 음악 기능
## DESCRIPTION: 음악 오브젝트의 생성, 조회, 수정, 삭제 기능을 제공합니다.
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////

class MusicDefineBody(BaseModel):
    title: str
    album_id: str | None = None
    length: int | None = None


@apis["v1"].post("/music/{id}/define", status_code=201, tags=["music", "define", "create"])
async def music_define_query(id: str, body: MusicDefineBody) -> dict[str, object]:
    """
    ## CREATE: 음악 오브젝트를 생성합니다.
    
    ### Request
    - `path parameter`
        - `id`: 음악 ID
    
    ### Response
    
    - `status code` 상태 설명
        - `201`: Message{"요청하신 음원을 생성했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `410`: HTTPException{"요청하신 음원을 생성할 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    try:
        with db.new_session() as session:
            session.add(DA.MusicTable(music_id=id, album_id=body.album_id, title=body.title, length=body.length))
            session.commit()
    except IntegrityError:
        raise HTTPException(status_code=410, detail="요청하신 음악은 이미 존재하는 음악입니다.")
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/music/{id}/info", tags=["music", "info", "read"])
async def music_info_query(id: str):
    """
    ## READ: 데이터베이스에서 기본적인 음원정보를 조회합니다.
    
    ### Request
    - `path parameter`
        - `id`: 음악 ID
    
    ### Response
    
    - `status code` 상태 설명
        - `200`: MusicGeneralInfo
        - `404`: HTTPException{"요청하신 음원을 찾을 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    # TODO: 음악 정보를 가져오는 코드를 작성하세요.
    with db.new_session() as session:
        try:
            music = session.exec(select(DA.MusicTable).where(DA.MusicTable.music_id == id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="요청하신 음악이 존재하지 않습니다.")
        return music
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/music/{id}/modify", response_model=None, tags=["music", "modify", "update"])
async def music_modify_query(id: str, body: MusicDefineBody) -> dict[str, object]:
    """
    ## UPDATE: 음악 오브젝트를 수정합니다.
    
    ### Request
    - `path parameter`
        - `id`: 음악 ID
    - `body`
        - `title`: 변경될 음악 제목, 선택사항입니다.
        - `album_id`: 변경될 앨범 아이디 정보, 선택사항입니다.
        - `length`: 변경될 음악 길이 정보, 선택사항입니다.
        
    ### Response
    
    - `status code` 상태 설명
        - `200`: Message{"요청하신 음원을 수정했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `403`: HTTPException{"요청하신 음원을 수정할 권한이 없습니다."}
        - `404`: HTTPException{"등록된 음원을 찾을 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
        
    """
    with db.new_session() as session:
        try:
            music = session.exec(select(DA.MusicTable).where(DA.MusicTable.music_id == id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="요청하신 음악이 존재하지 않습니다.")
        if body.title != None:
            music.title = body.title
        if body.album_id != None:
            music.album_id = body.album_id
        if body.length != None:
            music.length = body.length
        session.add(music)
        session.commit()
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].post("/music/{id}/remove", status_code=201, tags=["music", "remove", "delete"])
async def music_remove_query(id: str) -> dict[str, object]:
    """
    ## DELETE: 음악 오브젝트를 삭제합니다.
    
    ### Request
    - `path parameter`
        - `id`: 음악 ID
    
    ### Response
    
    - `status code` 상태 설명
        - `201`: Message{"요청하신 음원을 삭제했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `403`: HTTPException{"요청하신 음원을 삭제할 권한이 없습니다."}
        - `404`: HTTPException{"요청하신 음원을 찾을 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    with db.new_session() as session:
        try:
            music = session.exec(select(DA.MusicTable).where(DA.MusicTable.music_id == id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="요청하신 음악이 존재하지 않습니다.")
        session.delete(music)
        session.commit()
## ///////////////////////////////////////////////////////////////////////////////////////////////////////////
@apis["v1"].get("/partition/{id}/read", tags=["partition", "read"], response_class=FileResponse)
async def partition_read_query(id: str):
    """
    ## READ: 디스크에서 파티션 파일을 읽습니다.
    
    ### Request
    - `path parameter`
        - `id`: 파티션 ID
        
    ### Response
    
    - `body`: 파일 데이터
    
    """
    path = Path.home() / ".pws-restapi-server" / "partitions" / id
    if not path.exists():
        raise HTTPException(status_code=404, detail="요청하신 파티션이 존재하지 않습니다.")
    return FileResponse(path)

@apis["v1"].post("/partition/{id}/write", tags=["partition", "write"], response_model=None)
async def partition_write_query(id: str, file: UploadFile):
    """
    ## WRITE: 디스크에 파티션 파일을 쓰기합니다.
    
    ### Request
    - `path parameter`
        - `id`: 파티션 ID
    - `body`
        - `file`: 파티션 파일
        
    ### Response
    
    - `status code` 상태 설명
        - `201`: Message{"요청하신 파티션을 생성했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `410`: HTTPException{"요청하신 파티션을 생성할 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    media_type = "application/octet-stream"
    path = Path.home() / ".pws-restapi-server" / "partitions" / id
    if path.exists():
        raise HTTPException(status_code=410, detail="요청하신 파티션이 이미 존재합니다.")
    with path.open("wb") as f:
        f.write(file.file.read())
        f.close()

@apis["v1"].post("/partition/{id}/remove", tags=["partition", "remove"], response_model=None)
def partition_remove_query(id: str):
    """
    ## DELETE: 디스크에서 파티션 파일을 삭제합니다.
    
    ### Request
    - `path parameter`
        - `id`: 파티션 ID
        
    ### Response
    
    - `status code` 상태 설명
        - `201`: Message{"요청하신 파티션을 삭제했습니다."}
        - `400`: HTTPException{"잘못된 요청입니다."}
        - `410`: HTTPException{"요청하신 파티션을 삭제할 수 없습니다."}
        - `500`: HTTPException{"비정규 오류가 발생하여 요청을 처리하는데 실패했습니다."}
    
    """
    path = Path.home() / ".pws-restapi-server" / "partitions" / id
    if not path.exists():
        raise HTTPException(status_code=410, detail="요청하신 파티션이 존재하지 않습니다.")
    path.unlink()
    


# =============================================================================
# EOC: endpoints.py
# =============================================================================
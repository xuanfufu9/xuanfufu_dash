from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.online_vo import DeleteOnlineModel, OnlinePageQueryModel, OnlineQueryModel
from module_admin.service.login_service import LoginService
from module_admin.service.online_service import OnlineService
from utils.log_util import logger
from utils.page_util import PageResponseModel, PageUtil
from utils.response_util import ResponseUtil


onlineController = APIRouter(prefix='/monitor/online', dependencies=[Depends(LoginService.get_current_user)])


@onlineController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('monitor:online:list'))]
)
async def get_monitor_online_list(request: Request, online_page_query: OnlineQueryModel = Query()):
    # 获取全量数据
    online_query_result = await OnlineService.get_online_list_services(request, online_page_query)
    logger.info('获取成功')

    return ResponseUtil.success(
        model_content=PageResponseModel(rows=online_query_result, total=len(online_query_result))
    )


@onlineController.get(
    '/list/page',
    response_model=PageResponseModel,
    dependencies=[Depends(CheckUserInterfaceAuth('monitor:online:list'))],
)
async def get_monitor_online_page_list(request: Request, online_page_query: OnlinePageQueryModel = Query()):
    online_query = OnlineQueryModel(**online_page_query.model_dump(by_alias=True))
    # 获取全量数据
    online_query_result = await OnlineService.get_online_list_services(request, online_query)
    # 获取分页数据
    online_page_query_result = PageUtil.get_page_obj(
        online_query_result, online_page_query.page_num, online_page_query.page_size
    )
    logger.info('获取成功')

    return ResponseUtil.success(model_content=online_page_query_result)


@onlineController.delete('/{token_ids}', dependencies=[Depends(CheckUserInterfaceAuth('monitor:online:forceLogout'))])
@Log(title='在线用户', business_type=BusinessType.FORCE)
async def delete_monitor_online(request: Request, token_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_online = DeleteOnlineModel(token_ids=token_ids)
    delete_online_result = await OnlineService.delete_online_services(request, delete_online)
    logger.info(delete_online_result.message)

    return ResponseUtil.success(msg=delete_online_result.message)

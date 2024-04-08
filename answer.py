from rest_framework.response import Response
class frontend_error:
    """前端的問題"""
    def FormatError(error_log)-> Response:
        """輸出格式錯誤"""
        return Response(data="傳送格式出錯或資料有誤，錯誤訊息:{0}，請依照錯誤訊息進行修正".format(error_log), status=400)

    def KeyError() -> Response:
        """前端傳送的資料key找不到"""
        return Response(data=f"未依照格式傳送，請確認key是否符合API documetation所指示", status=400)

class backend_error:
    """後端的問題"""
    def accident(error_log)-> Response:
        """意外中錯誤"""
        return Response(status=500, data=f"發生意外中錯誤，請洽系統管理員，錯誤訊息:{error_log}")

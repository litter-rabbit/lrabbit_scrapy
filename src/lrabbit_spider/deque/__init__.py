

from typing import Callable, Tuple, Union,Any,List,Optional



class Dedup:
    
    BloomFilter = 1
    MemoryFilter = 2
    ExpireFilter = 3
    def __init__(self,filter_type:int=BloomFilter,to_md5:bool = True,**kwargs):
        pass
    def __repr__(self):
        pass

    def _deal_datas(self,datas):
        pass

    def add(self,datas:Union[List[Any],Any],skip_check:bool = False) -> Union[List[Any],Any]:
        pass
    def get(self,datas:Union[List[Any],Any]) -> Union[List[Any],Any]:
        pass

    # def filter_exist_data(
    #     self,datas:List[Any],
    #     *,
    #     datas_fingerprints:Options[List] = None,
    #     callback:Callable[[Any],None] = None) ->Union(Tuple[List[Any],List[Any],List[Any]]):
        
    #     pass
    def filter_exist_data(
            self,
            datas: List[Any],
            *,
            datas_fingerprints: Optional[List] = None,
            callback: Callable[[Any], None] = None
        ) -> Union[Tuple[List[Any], List[Any]], List[Any]]:
        pass

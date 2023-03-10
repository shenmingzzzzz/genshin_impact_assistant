from source.util import *
import keyboard
from pynput.keyboard import Listener, KeyCode, Key
from source.flow.flow_template import FlowController, FlowTemplate, FlowConnector, EndFlowTemplate
import source.flow.flow_code as FC, source.flow.flow_state as ST
from source.interaction.minimap_tracker import tracker
from source.controller import combat_loop
from source.common import timer_module
from source.funclib import generic_lib, movement, combat_lib
from source.funclib.err_code_lib import *
from source.manager import posi_manager as PosiM, asset
from source.interaction.interaction_core import itt


class PathRecorderConnector(FlowConnector):
    def __init__(self):
        super().__init__()


        self.total_collection_list = []
        self.checkup_stop_func = None
        self.collection_path_dict = {
            "time":"",
            "start_position":[],
            "end_position":[],
            "all_position":[],
            "position_list":[],
            "special_keys":[]
        }

        self.min_distance = 1
        self.listener = self.listener = Listener(on_press=self._add_key_to_dict)
        self.set_hotkey()
        '''
        Template:
        [
            {
                "name":"",
                "start_position":[],
                "end_position":[],
                "all_position":[
                    [point x, point y],
                    [point x, point y],
                    [point x, point y],
                    ...
                ],
                "position_list":[
                    {
                        "position":list,
                        "motion":str, include 'move'(or 'walk'), 'swim', 'climb', 'fly'.
                        "id":int
                    }, ...
                ],
                "special_keys":[
                    {
                        "position":list,
                        "key_name":str, include 'space', 'left click', 'left shift', 'x'.
                        "id":int
                    }, ...
                ]       
            }
        ...
        ]
        '''

    def set_hotkey(self):
        self.listener.start()
        # keyboard.add_hotkey("f", self._add_key_to_dict, args=('f',))
        # keyboard.add_hotkey("space", self._add_key_to_dict, args=('space',))
        # keyboard.add_hotkey("x", self._add_key_to_dict, args=('x',))
        # keyboard.add_hotkey("shift", self._add_key_to_dict, args=('shift',))

    def unset_hotkey(self):
        self.listener.stop()
        pass

    def _add_key_to_dict(self, key):
        if key == KeyCode.from_char('f'):
            key = 'f'
        elif key == Key.space:
            key = 'space'
        elif key == KeyCode.from_char('x'):
            key = 'x'
        elif key == Key.shift:
            key = 'shift'
        else:
            return
        curr_posi = tracker.get_position()
        self.collection_path_dict["special_keys"].append(
            {
                "position":list(curr_posi),
                "key_name":key,
                "id":len(self.collection_path_dict["special_keys"])+1
            }
        )
        logger.info(t2t("special key added:")+
                    str(key)
                    )


class PathRecorderCore(FlowTemplate):
    def __init__(self, upper: PathRecorderConnector):
        super().__init__(upper,flow_id=ST.PATH_RECORDER ,next_flow_id=ST.PATH_RECORDER_END)

        keyboard.add_hotkey('\\', self._start_stop_recording)

        self.upper = upper
        self.enter_flag = False

    def _add_posi_to_dict(self, posi:list):
        curr_motion = movement.get_current_motion_state()
        self.upper.collection_path_dict["position_list"].append(
            {
                "position":posi,
                "motion":curr_motion,
                "id":len(self.upper.collection_path_dict["position_list"])+1
            }
        )
        self.upper.collection_path_dict["all_position"].append(posi)
        logger.info(t2t("position added:")+
                    f"{posi} {curr_motion}"
                    )

    def state_init(self):
        pass
        # self._next_rfc()

    def state_before(self):

        self.upper.collection_path_dict = {
            "name":"",
            "start_position":[],
            "end_position":[],
            "all_position":[],
            "position_list":[],
            "special_keys":[]
        }
        self.enter_flag = False
        tracker.reinit_smallmap()
        self._next_rfc()

    def _start_stop_recording(self):
        if self.rfc == FC.INIT:
            self.rfc = FC.BEFORE
            logger.info(t2t("ready to start recording"))
        if self.rfc == FC.IN:
            self.rfc = FC.AFTER
            logger.info(t2t("stop recording"))


    def state_in(self):

        all_posi = self.upper.collection_path_dict["all_position"]
        curr_posi = tracker.get_position()
        if len(all_posi)>0:
            min_dist = quick_euclidean_distance_plist(curr_posi, all_posi).min()
        else:
            min_dist = 99999

        if min_dist >= self.upper.min_distance:
            self._add_posi_to_dict(list(curr_posi))

        if not self.enter_flag:
            logger.info(t2t("start recording"))
            self.enter_flag = True
        return super().state_in()

    def state_after(self):
        self.upper.total_collection_list.append(self.upper.collection_path_dict)

        self.rfc = FC.INIT


class PathRecorderEnd(EndFlowTemplate):
    def __init__(self, upper: FlowConnector):
        super().__init__(upper, flow_id=ST.PATH_RECORDER_END, err_code_id=ERR_PASS)

class PathRecorderController(FlowController):
    def __init__(self):
        super().__init__(PathRecorderConnector(), current_flow_id =  ST.PATH_RECORDER)
        self.flow_connector = self.flow_connector # type: PathRecorderConnector
        self.flow_connector.checkup_stop_func = self.checkup_stop_func

        self.append_flow(PathRecorderCore(self.flow_connector))   
        self.append_flow(PathRecorderEnd(self.flow_connector))

    def reset(self):
        pass

if __name__ == '__main__':
    PathRecorderController().start()
    while 1:
        time.sleep(1)
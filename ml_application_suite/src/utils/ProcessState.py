
import threading

class ProcessState:
    """

    """

    def __init__(self,states_sequence:list[str]):

        self.states_sequence = ['begin'] + states_sequence + ['end']
        self.current_state_index = 0
        self.stateUpdated_semaphore = threading.Semaphore(0)
        self.critic_section = threading.Lock()

    def initialize(self):
        self.current_state_index = 0
        self.stateUpdated_semaphore = threading.Semaphore(0)
        self.critic_section = threading.Lock()


    def pass_to_next_state(self):
        with self.critic_section:
            self.current_state_index += 1
            self.stateUpdated_semaphore.release()

    def set_fail_state(self):
        with self.critic_section:
            self.current_state_index = -1
            self.stateUpdated_semaphore.release()

    def get_new_state(self):
        self.stateUpdated_semaphore.acquire()

        return 'fail'\
            if self.current_state_index == -1\
            else self.states_sequence[self.current_state_index]



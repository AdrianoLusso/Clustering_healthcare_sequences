
import threading

class ProcessState:
    """

    """

    def __init__(self,states_sequence:list[str]):

        self.states_sequence = ['begin'] + states_sequence + ['end']
        self.stateUpdated_semaphore = threading.Semaphore(0)
        self.critic_section = threading.Lock()
        self.current_state_index = 0

    def pass_to_next_state(self):
        with self.critic_section:
            self.current_state_index += 1
            self.stateUpdated_semaphore.release()

    def get_new_state(self):
        self.stateUpdated_semaphore.acquire()
        return self.states_sequence[self.current_state_index]



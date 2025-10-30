
class StateMachine:
    def __init__(self, start_state, state_transitions):
        self.cur_state = start_state
        self.state_transitions = state_transitions
        self.cur_state.enter(('START', None))

    def update(self):
        self.cur_state.do()

    def handle_state_event(self, event):
        for check_event in self.state_transitions[self.cur_state].keys():
            if check_event(event):
                self.cur_state.exit(event)
                self.next_state = self.state_transitions[self.cur_state][check_event]
                self.next_state.enter(event)
                self.cur_state = self.next_state
                return


    def draw(self):
        self.cur_state.draw()

    def change_state(self, new_state, event = ('INTERNAL', None)):
        prev_state = self.cur_state
        self.cur_state.exit(event)
        new_state.enter(('STATE_CHANGE', prev_state))
        self.cur_state = new_state


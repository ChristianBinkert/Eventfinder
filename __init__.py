from mycroft import MycroftSkill, intent_file_handler


class Eventfinder(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('eventfinder.intent')
    def handle_eventfinder(self, message):
        self.speak_dialog('eventfinder')


def create_skill():
    return Eventfinder()


# confusion_set_channel.py

class ConfusionSetChannel():

    def __init__(self, random_number_generator, error_rate, confusion_set_function, output_method):

        self.random_number_generator = random_number_generator
        self.error_rate = error_rate
        self.confusion_set_function = confusion_set_function
        self.write = output_method
        self.tokens = 0
        self.errors = 0


    def accept_string(self, string):

        self.tokens += 1
        random_number = self.random_number_generator.random()

        if random_number >= self.error_rate:
            self.write(string)

        else:
            self.write(self.random_number_generator.choice(self.confusion_set_function(string)))
            self.errors += 1

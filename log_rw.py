from datetime import datetime


def write_log(res):
    with open('contact_log.log', 'a') as calc_log:
        curr_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        calc_log.write(f'{curr_time}:   {res}\n')


def read_log():
    with open('contact_log.log', 'r') as contact_log:
        line_out = ''
        for line in contact_log:
            line_out += line + '\n'
        print(line_out)
        return line_out

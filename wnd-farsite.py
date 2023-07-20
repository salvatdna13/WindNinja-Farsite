import argparse
import os
import sys
from subprocess import PIPE, Popen
import time

if __name__ == '__main__':
    start_time = time.time()
    parser = argparse.ArgumentParser(description='Processing the windfile with WindNinja', add_help=False)
    parser.add_argument('-h', '--help', action='help')
    parser.add_argument('-o', '--output', dest='output', type=str, help='Path of the output folder', default=os.getcwd())
    modes = parser.add_argument_group('modes')
    modes.add_argument('-w', '--windninja', dest='windninja', action='store_true')
    modes.add_argument('-nw', '--no-windninja', dest='windninja', action='store_false')
    modes.add_argument('-c', '--complex_wind', dest='mode', action='store_true')
    modes.add_argument('-s', '--simple_wind', dest='mode', action='store_false')
    modes.set_defaults(windninja=True, mode=True)
    files = parser.add_argument_group('files')
    files.add_argument('-wf', '--windfile', dest='windfile', type=str, help='Path of the windfile', required='--no-windninja' not in sys.argv and '-nw' not in sys.argv)
    files.add_argument('-cw', '--config_wnd', dest='config_wnd', type=str, help='Path of the WindNinja configuration file', required='--no-windninja' not in sys.argv and '-nw' not in sys.argv)
    files.add_argument('-cf', '--config_fars', dest='config_fars', type=str, help='Path of the farsite configuration file', required=True)
    args = parser.parse_args()
    
    atm_filename = 'case_1_100m.atm'
    if args.windninja:
        try:
            with open(args.windfile, 'r') as windfile:
                winds = []
                for line in windfile:
                    if 'ENGLISH' not in line and 'METRIC' not in line:
                        params = line[:-1].split(' ')
                        if len(params) != 6:
                            raise ValueError('Error: Alguna dada del fitxer de vents es incorrecta')
                        winds.append(params)
        except IOError:
            raise Exception("Error: No s'ha pogut llegir el fitxer de vents.")
        except ValueError as err:
            raise ValueError(str(err))
        
        atms = ['WINDS_AND_CLOUDS\nENGLISH\n']
        iter = 1
        total = len(winds)
        try:
            with open(args.config_wnd, 'r') as configfile:
                for line in configfile:
                    if 'out_resolution' in line and '#' not in line and 'units' not in line:
                        aux = line.split(' ')
                        out_resolution = aux[-1]
        except IOError:
            raise Exception("Error: No s'ha pogut llegir el fitxer de configuració.")
        print('Executant la generacio dels camps de vents')
        start_time_windninja = time.time()
        for wind in winds:
            start_time_local = time.time()
            month, day, hour, speed, direction, cover = wind
            try:        
                if args.output[-1] != '/':
                    args.output += '/'
                path = args.output + month + '-' + day + '-' + hour + '/'
                if not os.path.exists(path):
                    os.mkdir(path)
            except OSError:
                raise OSError("No s'ha pogut crear el directori de sortida")
            command = ['WindNinja_cli', args.config_wnd, '--output_path', path, '--num_threads', str(os.cpu_count()), '--month', month, '--day', day, 
                       '--hour', hour, '--input_speed', speed, '--input_direction', direction]
            result = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out, err = result.communicate()
            result.terminate()
            if err.decode() != '':
                raise ValueError(err.decode())
            try:
                with open(path + 'time_200m.txt', 'w') as time_file:
                    time_file.writelines(out.decode())
            except IOError:
                raise Exception("Error: No s'ha pogut crear el fitxer.")
            file = path + 'CASE_1_' + direction + '_' + speed + '_' + str(int(float(out_resolution))) + 'm_'
            atms.append(' '.join([month, day, hour, file + 'vel.asc', file + 'ang.asc', file + 'cld.asc\n']))
            end_time_local = time.time()
            print('(' + str(iter) + '/' + str(total) + '): ' + str(end_time_local-start_time_local) + ' s')
            iter += 1
        end_time_windninja = time.time()
        windninja_time = [int((end_time_windninja - start_time_windninja) / 60), (end_time_windninja - start_time_windninja) - 
                          int((end_time_windninja - start_time_windninja) / 60)*60]
        print('WindNinja time: ' + str(windninja_time[0]) + ' min i ' + str(windninja_time[1]) + ' s')
        try:
            with open(atm_filename, 'w') as atm_file:
                atm_file.writelines(atms)
        except IOError:
            raise Exception("Error: No s'ha pogut crear el fitxer de vents.")
    
    start_time_farsite = time.time()
    print('Executant Fariste')
    if args.mode:
        try:
            with open(args.config_fars, 'r+') as settings:
                settings_read = settings.readlines()
                for i in range(len(settings_read)):
                    if 'windFile0' in settings_read[i]:
                        aux = settings_read[i].split(' ')
                        aux[2] = args.output + '/' + atm_filename + '\n'
                        settings_read[i] = ' '.join(aux)
                settings.seek(0)
                settings.writelines(settings_read)
        except:
            raise Exception("No s'ha pogut llegir el fitxer de Settings.")

    else:
        try:
            with open(args.config_fars, 'r+') as settings:
                settings_read = settings.readlines()
                for i in range(len(settings_read)):
                    if 'windFile0' in settings_read[i]:
                        aux = settings_read[i].split(' ')
                        aux[2] = args.output + '/' + args.windfile + '\n'
                        settings_read[i] = ' '.join(aux)
                settings.seek(0)
                settings.writelines(settings_read)
        except:
            raise Exception("No s'ha pogut llegir el fitxer de Settings.")

    command = ['./farsite4P', '-i', args.config_fars, '-f', str(os.cpu_count())]
    result = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = result.communicate()
    result.terminate()
    if err.decode() != '':
        raise ValueError(err.decode())
    end_time = time.time()
    farsite_time = [int((end_time - start_time_farsite) / 60), (end_time - start_time_farsite) - int((end_time - start_time_farsite) / 60)*60]
    total_time = [int((end_time - start_time) / 60), (end_time - start_time) - int((end_time - start_time) / 60)*60]
    print('Farsite time: ' + str(farsite_time[0]) + ' min i ' + str(farsite_time[1]) + ' s')
    print('Total time: ' + str(total_time[0]) + ' min i ' + str(total_time[1]) + ' s')
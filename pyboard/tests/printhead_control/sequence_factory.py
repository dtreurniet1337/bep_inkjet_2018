import config

class SequenceFactory():
    """
    Nozzle selection and quality sequence generator
    Written by Daan Treurniet, april 3, 2018
    This class generates the clock, black and color data for printing.

    How to use:
    After instantiating a Sequence_factory object,
    everything is done with the get_sequence function.

    You can choose which nozzles fire with the following arguments:
    nozzles_black = [1,2,3,4,.......,87,88,89,90]
    nozzles_cyan = [1,2,3,4,........27,28,29,30]
    nozzles_magenta = [1,2,3,4,........27,28,29,30]
    nozzles_yellow = [1,2,3,4,........27,28,29,30]

    To choose droplet size, set the size argument to:
    'small', 'medium' or 'large'

    To set quality settings: set the quality argument to:
    'economy', 'VSD1', 'VSD2' or 'VSD3'

    The function will return a list of 16-bit words, with 6 bits of data.
    The placement of these bits is defined in the config file.
    """



    def __init__(self):
        pass

    def _nozzle_to_pulse_black(self, nozzle):
        if nozzle >= 61: return (30-(nozzle-60))*2+1
        if nozzle <= 30: return (116-nozzle)*2+1
        else: return (73-(nozzle-30))*2+1
    def _nozzle_to_pulse_cyan(self, nozzle): return (116-nozzle)*2+1
    def _nozzle_to_pulse_magenta(self, nozzle): return (73-(nozzle))*2+1
    def _nozzle_to_pulse_yellow(self, nozzle): return (30-(nozzle))*2+1

    def _get_selection_block(self,
                              nozzles_black, nozzles_cyan,
                              nozzles_yellow, nozzles_magenta):
        tmp_data_black = [0]*256
        tmp_data_color = [0]*256
        # Populate black nozzle data
        for nozzle_b in nozzles_black:
            tmp_data_black[self._nozzle_to_pulse_black(nozzle_b)] = 1
            tmp_data_black[self._nozzle_to_pulse_black(nozzle_b)+1] = 1
        # Populate color nozzle data
        for nozzle_c in nozzles_cyan:
            tmp_data_color[self._nozzle_to_pulse_cyan(nozzle_c)] = 1
            tmp_data_color[self._nozzle_to_pulse_cyan(nozzle_c)+1] = 1
        for nozzle_m in nozzles_magenta:
            tmp_data_color[self._nozzle_to_pulse_magenta(nozzle_m)] = 1
            tmp_data_color[self._nozzle_to_pulse_magenta(nozzle_m)+1] = 1
        for nozzle_y in nozzles_yellow:
            tmp_data_color[self._nozzle_to_pulse_yellow(nozzle_y)] = 1
            tmp_data_color[self._nozzle_to_pulse_yellow(nozzle_y)+1] = 1
        return (tmp_data_black, tmp_data_color)

    def _get_quality_sequence(self, quality):
        tmp_data = [0]*64

        if quality == 'economy': i_list = [40,50,52,54,56]
        if quality == 'VSD1': i_list = [24,26,32,36,40,42,48,62]
        if quality == 'VSD2': i_list = [28,32,40,48,50,62]
        if quality == 'VSD3': i_list = [36,40,48,50,62]

        for i in i_list:
            tmp_data[i] = 1
            tmp_data[i+1] = 1
        return tmp_data

    def _tuple_to_word_list(self, lists):
        signal_len = len(lists[0])
        signal = [0x0]*signal_len
        for i in range(signal_len):
            signal[i] |= (lists[0][i] << config.GPIO_CK)
            signal[i] |= (lists[1][i] << config.GPIO_SIBL)
            signal[i] |= (lists[2][i] << config.GPIO_SICL)
        return signal



    def get_sequence(self,
                     nozzles_black=[], nozzles_yellow=[],
                     nozzles_cyan=[], nozzles_magenta=[],
                     size='medium', quality='VSD2', plot=False):
        nozzles_black = list(nozzles_black)
        nozzles_cyan = list(nozzles_cyan)
        nozzles_magenta = list(nozzles_magenta)
        nozzles_yellow = list(nozzles_yellow)

        data_clock = [0,0]
        data_black = [0]
        data_color = [0]

        # PHASE 1: first selection of nozzles
        # Init clock and empty data lines
        for i in range(64):
            data_clock.extend([0,1,1,0])
        if size == 'large' or size == 'medium':
            tmp_data = self._get_selection_block(nozzles_black, nozzles_cyan, nozzles_yellow, nozzles_magenta)
            data_black.extend(tmp_data[0])
            data_color.extend(tmp_data[1])
        else:
            data_clock.append(0)
            data_black.extend([0]*256)
            data_color.extend([0]*256)

        # PHASE 2: insert waiting period
        for i in range(230):
            data_clock.append(0)
            data_black.append(0)
            data_color.append(0)

        # PHASE 3: second selection of nozzles
        for i in range(64):
            data_clock.extend([0,1,1,0])
        if size == 'large' or size == 'small':
            tmp_data = self._get_selection_block(nozzles_black, nozzles_cyan, nozzles_yellow, nozzles_magenta)
            data_black.extend(tmp_data[0])
            data_color.extend(tmp_data[1])
        else:
            data_black.extend([0]*256)
            data_color.extend([0]*256)

        # PHASE 4: insert waiting period
        for i in range(230):
            data_clock.append(0)
            data_black.append(0)
            data_color.append(0)

        # Phase 5: quality selection pulses
        for i in range(16):
            data_clock.extend([0,1,1,0])
        tmp_data = self._get_quality_sequence(quality)
        data_black.extend(tmp_data)
        data_color.extend(tmp_data)

        # Phase 6: append zeroes for good measure
        data_clock.append(0)
        data_black.append(0)
        data_black.append(0)
        data_color.append(0)
        data_color.append(0)


        if plot == True:
            self.fig, axarr = plt.subplots(3, 1, sharex=True)
            axarr[0].plot(range(len(data_clock)), data_clock, drawstyle='steps-pre')
            axarr[1].plot(range(len(data_black)), data_black, drawstyle='steps-pre')
            axarr[2].plot(range(len(data_color)), data_color, drawstyle='steps-pre')
            plt.show()

        return self._tuple_to_word_list((data_clock, data_black, data_color))

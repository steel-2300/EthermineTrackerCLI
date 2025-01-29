#!/usr/bin/python3

#####################################
#  Ethermine Tracker CLI           	#
#  main.py			        		#
#####################################

import configparser
import curses
import sys
from datetime import datetime
from time import sleep

import EthMiningFetcher as EMF

TERM_COLS = 80
TERM_CENT = TERM_COLS // 2
H_PROG_COLS = 60
TOP_ROW = '╔' + '═' * (TERM_COLS - 2) + '╗'
BOTTOM_ROW = '╚' + '═' * (TERM_COLS - 2) + '╝'
SEP_ROW = '╠' + '═' * (TERM_COLS - 2) + '╣'
END_ROW = '╚' + '═' * (TERM_COLS - 2) + '╝'
SIMPLE_SEP_ROW = '╟' + '─' * (TERM_COLS - 2) + '╢'
ARRAY_SEP_ROW = '╟' + '┄' * (TERM_COLS - 2) + '╢'
THREE_SEP_1 = int((TERM_COLS - 2) / 3)
THREE_SEP_2 = int((TERM_COLS - 2) / 3 * 2)
THREE_CENT_1 = int((THREE_SEP_1 - 1) / 2)
THREE_CENT_2 = int(((THREE_SEP_2 - THREE_SEP_1) / 2) + (THREE_SEP_1 + 1))
THREE_CENT_3 = int(((TERM_COLS - 1 - THREE_SEP_2) / 2) + (THREE_SEP_2 + 1))
HASH_CENT_1 = 6
HASH_CENT_2 = HASH_CENT_1 + 11
HASH_CENT_3 = HASH_CENT_2 + 11
HASH_CENT_4 = HASH_CENT_3 + 13
HASH_CENT_5 = HASH_CENT_4 + 13
HASH_CENT_6 = HASH_CENT_5 + 10
HASH_CENT_7 = HASH_CENT_6 + 10
HASH_CEP = [11, 11, 11, 16, 10, 10]
PAYOUT_CEP = [12, 16, 17, 17]
PAYOUT_CENT = [6, 14, 17, 17, 17]
PAYOUT_HEAD = ['Ref', 'By hour', 'By day', 'By week', 'By month']
ALERT_UPDATE_M = 15
PERC_DELTA_YELLOW = 0.02
PERC_DELTA_RED = 0.05
CRYPTO_S = 'ETH'

cfg_section = 'Tracker'


def get_config(option):
    if not config.has_option(cfg_section, option):
        print('Option ' + option + ' missing')
        return None
    if config[cfg_section][option] == '':
        print('Option ' + option + ' is empty')
        return None

    return config[cfg_section][option]


config = configparser.ConfigParser()
if len(config.read('config.cfg')) < 1:
    print('Config file not exist')
    print('Copy \'config_sample.cfg\' to \'config.cfg\' ', end='')
    print('and update with your value')
    exit(1)

wallet = get_config('Wallet')
etherscan_api_key = get_config('Etherscan_API')
fiat_name = get_config('Fiat_Name')
fiat_s = get_config('Fiat_symbol')
theorical_hrate = float(get_config('Theorical_hrate'))
api_update_sec = int(get_config('Api_Update_Seconds'))

if not all(v is not None for v in
           [wallet, etherscan_api_key, fiat_name, fiat_s,
            theorical_hrate, api_update_sec]):
    exit(1)


ethm = EMF.Ethermine(wallet)
coin = EMF.Coin(fiat_name, 'ethereum')
ethw = EMF.EtherWallet(etherscan_api_key, wallet)
ccalc_reported = EMF.CoinCalculators('ethereum')
ccalc_theorical = EMF.CoinCalculators('ethereum')


def update_data():
    ethm.update()
    coin.update()
    ethw.update()
    ccalc_reported.update(ethm.reported_hrate)
    ccalc_theorical.update(theorical_hrate)
    ethm.update_next_payout(ethm.eth_pay_stats.eth_hour)


def display_ext_border(y_start):
    stdscr.addstr(y_start, 0, '║')
    stdscr.addstr(y_start, TERM_COLS - 1, '║')


def display_separator(y_start, type_sep=SEP_ROW):
    stdscr.addstr(y_start, 0, type_sep)


def display_title(y_start, text, color=0):
    display_ext_border(y_start)
    stdscr.addstr(y_start, TERM_COLS // 2 - len(text) // 2, text,
                  curses.color_pair(color))


def dis_value(y_start, x_middle, label, value='',
              value_color=0, unit='', label_color=0, sep=': ',
              sep_color=0, unit_color=0):
    sep = '' if (value == '' or label == '') else sep
    global_len = len(str(label)) + len(str(value)) + len(unit) + len(sep)
    label_start = x_middle - (global_len // 2)
    value_start = label_start + len(str(label)) + len(sep)
    unit_start = value_start + len(str(value)) + 1
    stdscr.addstr(y_start, label_start, str(label),
                  curses.color_pair(label_color))
    stdscr.addstr(y_start, label_start + len(str(label)), sep,
                  curses.color_pair(sep_color))
    stdscr.addstr(y_start, value_start, str(value),
                  curses.color_pair(value_color))
    stdscr.addstr(y_start, unit_start, unit, curses.color_pair(unit_color))


def dis_hrate_avg(y_start, x_middle, val1, col1, val2, col2, val3, col3,
                  col_sep=0, sep='/'):
    global_len = len(str(val1)) + len(str(val2)) + len(str(val3)) + \
        (2 * len(sep))
    x_val1 = x_middle - (global_len // 2)
    x_sep1 = x_val1 + len(str(val1))
    x_val2 = x_sep1 + len(sep)
    x_sep2 = x_val2 + len(str(val2))
    x_val3 = x_sep2 + len(sep)
    stdscr.addstr(y_start, x_val1, str(val1), curses.color_pair(col1))
    stdscr.addstr(y_start, x_sep1, sep, col_sep)
    stdscr.addstr(y_start, x_val2, str(val2), curses.color_pair(col2))
    stdscr.addstr(y_start, x_sep2, sep, col_sep)
    stdscr.addstr(y_start, x_val3, str(val3), curses.color_pair(col3))


def split_three_col(y_start):
    stdscr.addstr(y_start, THREE_SEP_1, '┆')
    stdscr.addstr(y_start, THREE_SEP_2, '┆')


def to_cval(crypto_val):
    cval_f = round(crypto_val * coin.price, 2)
    return ('%.2f' % cval_f)


def eth(value):
    return ('%.5f' % value)


def fiat(value):
    return ('%.2f' % value)


def hrate(value):
    return ('%.2f' % value)


def hrateavg(value):
    return str(int(round(value, 0)))


def display_ethereum_infos(y_start):
    display_title(y_start, 'Ethereum informations', 2)
    delta = datetime.now().astimezone() - coin.last_update
    time_col = 5 if delta.seconds < (60 * ALERT_UPDATE_M) else 1
    stdscr.addstr(y_start, TERM_COLS - 2 - len(coin.last_update_txt),
                  coin.last_update_txt, curses.color_pair(time_col))
    y_start += 1
    display_ext_border(y_start)
    split_three_col(y_start)
    change_col = 3 if coin.pc_24h > 0 else 1
    dis_value(y_start, THREE_CENT_1, 'Price',
              fiat(coin.price), change_col, fiat_s)
    dis_value(y_start, THREE_CENT_2, 'Change 24H',
              fiat(coin.pc_24h), change_col, fiat_s)
    dis_value(y_start, THREE_CENT_3, 'ATH', fiat(coin.ath), 0, fiat_s)

    return y_start + 1


def report_color(actual, histo):
    cap_histo_yellow = histo * (1 - PERC_DELTA_YELLOW)
    cap_histo_red = histo * (1 - PERC_DELTA_RED)
    if actual >= cap_histo_yellow:
        return 3
    if actual > cap_histo_red:
        return 4
    return 1


def display_array_line_sep(y_start, tab_ref, top=False, end=False, gend=False):
    if top:
        sep_char = '┬'
        sep_line = SIMPLE_SEP_ROW
    elif end:
        sep_char = '┴'
        sep_line = SIMPLE_SEP_ROW
    elif gend:
        sep_char = '╧'
        sep_line = END_ROW
    else:
        sep_char = '┼'
        sep_line = ARRAY_SEP_ROW

    display_separator(y_start, sep_line)
    x_index = 0
    for index in range(len(tab_ref)):
        x_index = tab_ref[index] if index == 0 \
            else x_index + tab_ref[index]
        stdscr.addstr(y_start, x_index, sep_char)

    return y_start + 1


def display_hash_array_headers(y_start, workers=False):
    display_ext_border(y_start)
    dis_value(y_start, HASH_CENT_1, 'Worker' if workers else 'Period')
    dis_value(y_start, HASH_CENT_2, 'Report')
    dis_value(y_start, HASH_CENT_3, 'Actual')
    dis_value(y_start, HASH_CENT_4,
              'Avg 1/6/12H' if workers else 'Avg 1/6/24H')
    dis_value(y_start, HASH_CENT_5, 'Valid')
    dis_value(y_start, HASH_CENT_6, 'Stale')
    dis_value(y_start, HASH_CENT_7, 'Inval')
    return y_start + 1


def display_hash_array_line(y_start, title, ref, histo_id=0, col_force=None):
    histo_ref = ref.max_index - (histo_id * 3)
    reported_hrate = ref.stats_histo[histo_ref].reported_hrate
    current_hrate = ref.stats_histo[histo_ref].current_hrate
    valid_shares = ref.stats_histo[histo_ref].valid_shares
    stale_shares = ref.stats_histo[histo_ref].stale_shares
    invalid_shares = ref.stats_histo[histo_ref].invalid_shares

    color = [0] * 9
    if col_force is None:
        color[1] = report_color(reported_hrate, ref.last_histo.reported_hrate)
        color[2] = report_color(current_hrate, reported_hrate)
        color[3] = report_color(ref.avg_hrate_1[histo_id], reported_hrate)
        color[4] = report_color(ref.avg_hrate_6[histo_id], reported_hrate)
        color[5] = report_color(ref.avg_hrate_24[histo_id], reported_hrate)
        color[6] = report_color(valid_shares, ref.last_histo.valid_shares)
        color[7] = 4 if stale_shares > 0 else 3
        color[8] = 1 if invalid_shares > 0 else 3
    else:
        color = [col_force] * 9

    display_ext_border(y_start)
    dis_value(y_start, HASH_CENT_1, '', title, color[0])
    dis_value(y_start, HASH_CENT_2, '', hrate(reported_hrate), color[1])
    dis_value(y_start, HASH_CENT_3, '', hrate(current_hrate), color[2])
    dis_hrate_avg(y_start, HASH_CENT_4,
                  hrateavg(ref.avg_hrate_1[histo_id]), color[3],
                  hrateavg(ref.avg_hrate_6[histo_id]), color[4],
                  hrateavg(ref.avg_hrate_24[histo_id]), color[5], color[0])
    dis_value(y_start, HASH_CENT_5, '', valid_shares, color[6])
    dis_value(y_start, HASH_CENT_6, '', stale_shares, color[7])
    dis_value(y_start, HASH_CENT_7, '', invalid_shares, color[8])

    return y_start + 1


def display_hash_array(y_start, workers=False):
    y_start = display_array_line_sep(y_start, HASH_CEP, True)
    y_start = display_hash_array_headers(y_start)
    y_start = display_array_line_sep(y_start, HASH_CEP)

    if len(ethm.stats_histo) > 6:
        y_start = display_hash_array_line(y_start, 'Actual', ethm)
        y_start = display_hash_array_line(y_start, '30 min', ethm, 1, 5)
        y_start = display_hash_array_line(y_start, '60 min', ethm, 2, 5)

    y_start = display_array_line_sep(y_start, HASH_CEP, False, True)
    return y_start


def display_workers(y_start):
    y_start = display_array_line_sep(y_start, HASH_CEP, True)
    y_start = display_hash_array_headers(y_start, True)
    y_start = display_array_line_sep(y_start, HASH_CEP, False)

    for worker in ethm.workers:
        if len(worker.stats_histo) > 6:
            y_start = display_hash_array_line(y_start, worker.name, worker)
            y_start = display_hash_array_line(y_start, '30 min', worker, 1, 5)
            y_start = display_hash_array_line(y_start, '60 min', worker, 2, 5)

    y_start = display_array_line_sep(y_start, HASH_CEP, False, False, True)
    return y_start


def report_color_tresh(value, tresh1, tresh2):
    color = 0
    if value >= tresh1 * (1 - PERC_DELTA_YELLOW):
        color = 3
    elif value >= tresh2 * (1 - PERC_DELTA_RED):
        color = 4
    else:
        color = 1

    return color


def display_payout_array_headers(y_start):
    display_ext_border(y_start)
    x_index = 0
    for index in range(len(PAYOUT_HEAD)):
        x_index = PAYOUT_CENT[index] if index == 0 \
            else x_index + PAYOUT_CENT[index]
        dis_value(y_start, x_index, PAYOUT_HEAD[index])

    return y_start + 1


def display_payout_array_line(y_start, title, actual_ref, col_force=None,
                              reported_ref=None, theorical_ref=None):
    color = [0] * 5
    if col_force is None and reported_ref is not None \
            and theorical_ref is not None:
        color[1] = report_color_tresh(actual_ref.eth_hour,
                                      reported_ref.eth_hour,
                                      theorical_ref.eth_hour)
        color[2] = report_color_tresh(actual_ref.eth_day,
                                      reported_ref.eth_day,
                                      theorical_ref.eth_day)
        color[3] = report_color_tresh(actual_ref.eth_week,
                                      reported_ref.eth_week,
                                      theorical_ref.eth_week)
        color[4] = report_color_tresh(actual_ref.eth_month,
                                      reported_ref.eth_month,
                                      theorical_ref.eth_month)

    elif col_force is not None:
        color = [col_force] * 5

    eth_val = ['', actual_ref.eth_hour, actual_ref.eth_day,
               actual_ref.eth_week, actual_ref.eth_month]
    fiat_val = ['', to_cval(actual_ref.eth_hour), to_cval(actual_ref.eth_day),
                to_cval(actual_ref.eth_week), to_cval(actual_ref.eth_month)]

    display_ext_border(y_start)
    x_index = 0
    for index in range(len(PAYOUT_HEAD)):
        if index == 0:
            x_index = PAYOUT_CENT[index]
            dis_value(y_start, x_index, '', title, color[index])
        else:
            x_index += PAYOUT_CENT[index]
            dis_value(y_start, x_index, eth(eth_val[index]),
                      fiat_val[index], color[index], '', color[index], '/')

    return y_start + 1


def display_payout(y_start):
    display_separator(y_start, SIMPLE_SEP_ROW)
    stdscr.addstr(y_start, int(TERM_COLS / 2), '┬')

    y_start += 1
    display_ext_border(y_start)
    unpaid_text = 'Unpaid: ' + eth(ethm.unpaid_balance) + ' ' + CRYPTO_S
    unpaid_text += ' (' + str(to_cval(ethm.unpaid_balance)) + \
                   ' ' + fiat_s + ')'
    dis_value(y_start, int(TERM_COLS / 4), unpaid_text)
    tresh_text = 'Threshold: ' + eth(ethm.min_payout) + ' ' + CRYPTO_S
    tresh_text += ' (' + str(to_cval(ethm.min_payout)) + ' ' + fiat_s + ')'
    dis_value(y_start, int(TERM_COLS / 4 * 3), tresh_text)

    y_start += 1
    display_separator(y_start, SIMPLE_SEP_ROW)
    stdscr.addstr(y_start, int(TERM_COLS / 2), '┼')
    y_start += 1
    display_ext_border(y_start)
    last_text = 'Last payout: ' + ethm.payouts[0].paid_on_txt
    dis_value(y_start, int(TERM_COLS / 4), last_text)
    next_text = 'Next payout: ' + ethm.next_payout_txt
    dis_value(y_start, int(TERM_COLS / 4 * 3), next_text)

    y_start += 1
    display_ext_border(y_start)
    if ethm.gain_progress < 1:
        num_block = \
            int(round(ethm.gain_progress * 100 * (H_PROG_COLS / 100), 0))
        progress_text = str(round(ethm.gain_progress * 100, 1)).rjust(5, ' ')
    else:
        num_block = H_PROG_COLS
        progress_text = '100%'
    progress_string = '█' * num_block
    progress_string += '░' * (H_PROG_COLS - num_block)
    progress_string += ' ' + progress_text + '%'
    dis_value(y_start, int(TERM_COLS / 2), progress_string)

    y_start += 1
    y_start = display_array_line_sep(y_start, PAYOUT_CEP, True)
    y_start = display_payout_array_headers(y_start)
    y_start = display_array_line_sep(y_start, PAYOUT_CEP)

    y_start = display_payout_array_line(
        y_start, 'Estimated', ethm.eth_pay_stats, None,
        ccalc_reported.eth_pay, ccalc_theorical.eth_pay)
    y_start = display_payout_array_line(
        y_start, 'Reported', ccalc_reported.eth_pay, 5)
    y_start = display_payout_array_line(
        y_start, 'Theorical', ccalc_theorical.eth_pay, 5)
    y_start = display_payout_array_line(
        y_start, 'From last', ethm.eth_pay_from_last, 5)

    y_start = display_array_line_sep(y_start, PAYOUT_CEP, False, True)

    return y_start


def display_ethermine_pool(y_start):
    display_title(y_start, 'Ethermine informations', 2)
    delta = datetime.now().astimezone() - ethm.stat_time
    time_col = 5 if delta.seconds < (60 * ALERT_UPDATE_M) else 1
    stdscr.addstr(y_start, TERM_COLS - 2 - len(ethm.stat_time_txt),
                  ethm.stat_time_txt, curses.color_pair(time_col))
    display_ext_border(y_start + 1)
    state_col = 3 if ethm.pool_state == 'OK' else 1
    dis_value(y_start + 1, TERM_CENT, 'Status', ethm.pool_state, state_col)

    y_start += 2
    y_start = display_payout(y_start)
    y_start = display_hash_array(y_start)
    return y_start + 1


def display_header(y_start):
    display_title(y_start, '* Ethermine tracker *', 2)
    y_start += 1
    display_ext_border(y_start)
    dis_value(y_start, TERM_CENT, '', wallet)
    y_start += 1
    display_ext_border(y_start)
    wallet_text = str(ethw.balance) + ' ' + CRYPTO_S
    wallet_value = to_cval(ethw.balance)
    wallet_text += ' (' + str(wallet_value) + ' ' + fiat_s + ')'
    dis_value(y_start, TERM_CENT, '', wallet_text)
    return y_start + 1


def update_screen():
    stdscr.clear()
    y_start = 0
    display_separator(y_start, TOP_ROW)

    y_start += 1
    y_start = display_header(y_start)
    display_separator(y_start)

    y_start += 1
    y_start = display_ethereum_infos(y_start)
    display_separator(y_start)

    y_start += 1
    y_start = display_ethermine_pool(y_start)

    y_start -= 1
    y_start = display_workers(y_start)

    stdscr.move(y_start, 0)
    stdscr.refresh()


if __name__ == "__main__":
    print('Fetching data...')
    update_data()

    stdscr = curses.initscr()
    stdscr.nodelay(1)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, 244, curses.COLOR_BLACK)  # Grey medium

    update_screen()
    loop_index = 0
    while True:
        if loop_index == api_update_sec:
            stdscr.addstr(1, TERM_COLS - 12, 'Updating...',
                          curses.color_pair(5))
            stdscr.refresh()
            update_data()
            loop_index = 0
            update_screen()
        else:
            loop_index += 1

        countdown = str(api_update_sec - loop_index).rjust(11, ' ')
        stdscr.addstr(1, TERM_COLS - len(countdown) - 1,
                      countdown, curses.color_pair(5))
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key < 0:
            sleep(1)

    curses.endwin()
    sys.exit(0)

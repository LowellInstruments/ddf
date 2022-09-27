import csv
import glob
import os


# how to synchronize bucket from shell
#   $ mkdir bkt-cfa && cd bkt-cfa ---> do it or regret it
#   $ AWS_ACCESS_KEY_ID=<K> AWS_SECRET_ACCESS_KEY=<S> aws s3 sync s3://bkt-cfa .


_g_num_fusion_files = 0
_g_bkt_name = 'bkt-cfa'


def fusion_li_files(tf: str, pf: str, _rm=False):

    """
    Accepts 2 paths containing temperature and
    pressure in Lowell Instruments (*.lid) format and generates
    1 output file according to ODN format.
    If parameter _rm is set, deletes a pre-existing output file
    """

    # banner
    s = '\nrunning fusion algorithm for files:\n{}\n{}'
    print(s.format(tf, pf))

    # check we have files to fusion
    if not os.path.exists(tf):
        e = 'error fusion: temperature file {} does not exist'
        print(e.format(tf))
        return 1
    if not os.path.exists(pf):
        e = 'error fusion: pressure file {} does not exist'
        print(e.format(pf))
        return 1

    # generate dictionary from temperature csv file
    with open(tf, 'r') as f:
        rd = csv.reader(f)
        dt = {row[0]: row[1] for row in rd}

    # generate dictionary from pressure csv file
    with open(pf, 'r') as f:
        rd = csv.reader(f)
        dp = {row[0]: row[1] for row in rd}

    # discard too small files
    if len(dt) < 2 or len(dp) < 2:
        print('error fusion: files too small')
        return 2

    # del first key (headers) from each dictionary
    del dt['ISO 8601 Time']
    del dp['ISO 8601 Time']

    # checks fusion output file, 'F' denotes fusion
    prefix = tf.split('_Temperature')[0]
    o_name = prefix + '_FUSION_Temperature_Pressure.csv'
    if os.path.exists(o_name):
        if not _rm:
            e = 'error: output fusion file {} pre-exists, bye'
            print(e.format(o_name))
            return 3
        s = 'fusion file {} pre-exists, deleting it'
        print(s.format(o_name))
        os.unlink(o_name)

    # creates fusion output file
    f = open(o_name, 'w')
    f.write('Date,Time,Depth Decibar,Temperature C\n')
    for k, v in dt.items():
        # only grab common timestamps in both files
        if k in dp:
            yyyy_mm_dd, hh_mm_ss_ms = k.split('T')
            _ = yyyy_mm_dd.split('-')
            dd_mm_yyyy = '{}/{}/{}'.format(_[2], _[1], _[0])
            hh_mm_ss = hh_mm_ss_ms.split('.')[0]
            s = '{},{},{},{}\n'
            p_v = '{:.1f}'.format(float(dp[k]))
            t_v = '{:.3f}'.format(float(dt[k]))
            f.write(s.format(dd_mm_yyyy, hh_mm_ss, p_v, t_v))
    f.close()
    print('generated fusion file:\n{}'.format(o_name))
    global _g_num_fusion_files
    _g_num_fusion_files += 1


# run it
if __name__ == '__main__':
    glob_mask = '{}/{}/**/*_Temperature.csv'.format(os.getcwd(), _g_bkt_name)
    print('running with glob_mask ->', glob_mask)

    _ff = glob.glob(glob_mask, recursive=True)
    for _tf in _ff:
        _pf = _tf.replace('_Temperature', '_Pressure')
        try:
            fusion_li_files(_tf, _pf, _rm=True)
        except (Exception, ) as _ex:
            print('exception', _ex)

    _s = '\nsummary: generated {} fusion files'
    print(_s.format(_g_num_fusion_files))

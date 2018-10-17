from common import *


proxyon = True
url = "http://dvwa.vuln.lan.quillshome.com/"


def cmdreq(line: str, dvwa: packetvalues, baseline: str):
    z = webcoms(proxyon, args.ssl)    # setup of client class
    z.setup(url)            # setting up client for specified url
    i = 0
    for x in dvwa.data:
        if '$$' in x:
            tmp = re.split('\$\$', x)
            dvwa.data[i] = tmp[0] + line.strip('\n') + tmp[1]
        i += 1

    z.request(dvwa)
    rp = z.conn.getresponse()
    x = rp.read()

    if x == baseline:
        print('[-] ' + line.strip('\n'))
        print('[-] code: %s\tsize: %s' % (rp.code, len(x)))
    else:
        print('[+] ' + line.strip('\n'))
        print('[+] code: %s\tsize: %s' % (rp.code, len(x)))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    #parser.add_argument('-t', type=str, required=True, help="The url of the target excluding the path\nhttps://www.google.com:80\nhttp://192.168.1.15")
    #parser.add_argument('-p', type=bool, help="set this flag to use proxy", default=False)
    parser.add_argument('--ssl', default=False, type=bool)
    parser.add_argument('-f', dest="filename", help="Input payload file path", metavar="FILE",
                        type=lambda x: is_valid_file(parser, x))

    args = parser.parse_args()

    dvwa = packetvalues()
    dvwa.burpread(args.filename)
    cmdusg = Usage(4)

    h = webcoms(proxyon, args.ssl)    # setup of client class
    h.setup(url)            # setting up client for specified url

    insert = url.split('$$')
    cleandata = dvwa.data.copy()
    i = 0
    for x in dvwa.data:
        if '$$' in x:
            tmp = re.split('\$\$', x)
            dvwa.data[i] = tmp[0] + 'sfastwsaf'+ tmp[1]
        i += 1

    h.request(dvwa)
    rp = h.conn.getresponse()
    baseline = rp.read()
    j=0

    for line in open('/opt/wordlists/web-testing/cmd_injection.txt', 'r'):
        dvwa.data = cleandata.copy()
        cmdusg.multiproc(cmdreq, (line, dvwa, baseline))
        #cmdreq(line, dvwa, baseline)
        j += 1

    input()






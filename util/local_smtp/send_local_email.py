#!/usr/bin/python

import smtplib
import argparse


def cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', type=str)
    parser.add_argument('-to', type=str, nargs='+')
    return parser.parse_args()


def send(receivers, message, sender = 'test@localhost.com'):
    """
    send e-mail from localhost
    :param receivers: list of email addrs
    :param message:
    :param sender:
    :return:
    """
    try:
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, receivers, message)
        print("Successfully sent email")
    except Exception as e:
        print("Error: unable to send email:", e)

if __name__ == '__main__':
    args = cmd()
    print(args.m)
    print(args.to)
    send(args.to, args.m)

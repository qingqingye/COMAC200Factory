#!/bin/bash
ps -ef |grep SFServer.py  |awk '{print $2}'|xargs kill -9

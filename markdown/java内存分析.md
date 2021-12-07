```shell
# 线程情况
ps p 16494 -L -o pcpu,pmem,pid,tid,time,tname,cmd
# TID=17417的线程进行分析
[root@localhost ~]# printf "%x\n" 17417
4409
# 查看内存堆栈信息
jstack -l 16494 > jstack.log
```

XX:MaxPermSize设置过小会导致java.lang.OutOfMemoryError: PermGen space 就是内存益出
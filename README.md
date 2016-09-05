```
$ ssh my-cool-app
Permission denied (publickey).
```

Dammit.  
So you somehow mixed up your ssh keys and now you can't connect.  
Which key is the right one?  
Let's just try them all and update ~/.ssh/config with the one that works.  
Also, let's set proper permissions while we're at it.  

`python ssh_fixer.py`

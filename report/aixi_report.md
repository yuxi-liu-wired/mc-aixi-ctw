---
title: AIXI project, Semester 2, 2019
author: Andrew Tanggara, Yan Yang, Jiayan Liu, Changle Ye, Wenxi Wu, Yuxi Liu
date: October 2019
---

This isn't blue \textcolor{blue}{This is some blue text} This isn't blue
m
### Title and header metadata


### Pictures

![test image](test.jpg){width=50%}

### Tables


### Quotation and typographies

hyphen-endash--emdash---

The French and Indian War (1754–1763) was fought in western Pennsylvania and along the present US–Canada border (Edwards, pp. 81–101).

Horizontal lines
---

ligatures: ff, fi, fl, ffi, and ffl

elips...

'one quote' "two quotes"

### Codeblock

Some code:
```bash
#!/bin/bash
# argument is list of filters
FILTERS=$*
let err=0
for d in $FILTERS ; do
    make --no-print-directory -C $d test
    if [ $? -eq 0 ]; then
	err=1
    fi
done
exit $err
```
The fucking dash is wrong but I don't care for now.

### Word replacement

(c) (C) (r) (R) (tm) (TM) (p) (P) +-
© © ® ® ™ ™ § § ±

### Math demo {#my_head2}

$a^2 + b^2 = c^2$

$d/(dx) (int_0^x f(t)dt) = f(x)$

$$sum_(i=1)^n i^3=((n(n+1))/2)^2$$



### Citation demo

[@venessMonteCarloAIXI2009]

$$a^2 + b^2 = c^2$$ {#eq:description}

As Equation (@eq:description) says, ...

(@bar)  $e = x + y$

# Bibliography

Please click [](#my_head2) to go.

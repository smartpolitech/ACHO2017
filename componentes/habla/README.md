# HABLA
Habla process a string in order to determinate if 

Habla only need to recive one argument in order to begin its execution. 

## Configuration parameters
As any other component,
``` *habla* ```
needs a configuration file to start. In

    etc/config

you can find an example of a configuration file. We can find there the following lines:

    EXAMPLE HERE

    
## Starting the component
To avoid changing the *config* file in the repository, we can copy it to the component's home directory, so changes will remain untouched by future git pulls:

    cd

``` <habla 's path> ```

    cp etc/config config
    
After editing the new config file we can run the component:

    bin/

```habla ```

    --Ice.Config=config



## Functions

Habla count with different functions 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**readDic()**: open the file "dicc.txt". This file has the list of commands that ACHO can execute. The structure of the commands must be: 

VERB:AGENT,AGENT,AGENT,...
   
VERB:AGENT,AGENT,AGENT,...

Note: is important not to have blank spaces between chraracters.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**traduccion(message)**: traduce the command given -from any language- to English. If the traduction throws an error (For more information refer to: [TextBlobErrors](http://textblob.readthedocs.io/en/dev/_modules/textblob/exceptions.html))

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**srl(sen_dest)**: 


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**verb_noun(sen_srl)**: 



&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**match(sen)**: 



&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**result(command,data)**: 


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**procesa(message)**: 









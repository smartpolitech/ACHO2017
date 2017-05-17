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


&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.&nbsp;&nbsp;**procesa(message)**:&nbsp;&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.&nbsp;&nbsp;**traduccion(message)**:&nbsp;&nbsp;Traduce the command given -from any language- to English. If the traduction is not posible, the execution will be stoped here and ask for another command. This traduction is necessary in order to do the semantic role labeling to the command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(For more information refer to: [TextBlob Errors](http://textblob.readthedocs.io/en/dev/_modules/textblob/exceptions.html))

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.&nbsp;&nbsp;**srl(sen_dest)**:&nbsp;&nbsp;Using the library [practnlptools](https://pypi.python.org/pypi/practnlptools/1.0) based on the [SENNA](http://ronan.collobert.com/senna/) software, this function do the semantic role labeling on the translated command in order to find the verb to execute and the agent.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4.&nbsp;&nbsp;**verb_noun(sen_srl)**:&nbsp;&nbsp;A command is composed by a verb and an agent in which the action will be done. This function recive the semantic role labeled sentence throwed by the action before and -based on the analysis done by the software- determine if the command was given in a correct form. If not, the execution will be stoped here in order to ask for a correct command. 

If the command was correct, the function will split from the command only the verb and agent.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5.&nbsp;&nbsp;**match(sen)**:&nbsp;&nbsp;Retrieving the verb and agent from the function before, this function compare the verb from the command with the verb in the [dictionary](readDic())

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.&nbsp;&nbsp;**result(command,data)**:&nbsp;&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-&nbsp;&nbsp;**readDic()**:&nbsp;&nbsp;Open the file "dicc.txt". This file has the list of commands that ACHO can execute. The structure of the commands must be: 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VERB:AGENT,AGENT,AGENT,...
   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VERB:AGENT,AGENT,AGENT,...

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: is important not to have blank spaces between chraracters.

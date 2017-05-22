# HABLA
*Habla* determines if a command given could be executed by ACHO. That is to say, if the command is in the actions list that can be perform.
*Habla*s only argument is a string based on the command given.


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
*Habla* has many functions that help the correct execution of the component:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.&nbsp;&nbsp;**procesa(message)**:&nbsp;&nbsp;Is the main function in the component. The result is a structure composed by a boolean and a string. The boolean will be *True* if the execution was completed successfully or *False* if an error was encountered.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.&nbsp;&nbsp;**traduccion(message)**:&nbsp;&nbsp;Traduces the command given -from any language- to English. If the traduction is not posible, the execution will be stoped here and ask for another command. This traduction is necessary in order to do the semantic role labeling to the command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(For more information refer to: [TextBlob Errors](http://textblob.readthedocs.io/en/dev/_modules/textblob/exceptions.html))

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3.&nbsp;&nbsp;**srl(sen_dest)**:&nbsp;&nbsp;Using the library [practnlptools](https://pypi.python.org/pypi/practnlptools/1.0) based on the [SENNA](http://ronan.collobert.com/senna/) software, this function does the semantic role labeling on the translated sentence in order to find the verb and the agent with the purpose of retrieving only the principal sense of the command.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4.&nbsp;&nbsp;**verb_noun(sen_srl)**:&nbsp;&nbsp;A command is composed by a verb and an agent in which the action will be done. This function recives the semantic role labeled sentence throwed by the function before and -based on the analysis done by the software- determines if the command was given in a correct form (i.e. it has a verb and a noun). If not, the execution will be stopped here in order to ask for a correct command. 

If the command was correct, the function will split from the command only the verb and the agent.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5.&nbsp;&nbsp;**match(sen)**:&nbsp;&nbsp;Does a comparation between the retrieved verb from the function before and each verb in the dictionary. Returns the verb in the dictionary that is most similar and its ratio of similarity. *Does the same for the retrieved noun*.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;5.1&nbsp;&nbsp;**readDic()**:&nbsp;&nbsp;Opens the file "dicc.txt". This file has the list of commands that ACHO can execute. The structure of the commands must be: 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VERB:AGENT,AGENT,AGENT,...

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Note: is important not to have blank spaces between characters.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;6.&nbsp;&nbsp;**result(command,data)**:&nbsp;&nbsp;Based on the ratio of similarity of the noun and verb the result could throw three different choices:
If the ratio is greater or equal than 0.8, means that the command given is in the repertory of commands and therefore the command will be executed.
If the ratio is greater or equal than 0.6, means that there's a command similar in the repertory and therefore the component will show the user an alternative option of the command given at first.
If the ratio is less than 0.6, means that the command given is not in the repertory and therefore neither an execution nor an option could be thrown.

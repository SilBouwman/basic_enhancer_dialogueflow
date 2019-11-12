# basic_enhancer_dialogueflow
This repo helps to let dialogueflow deal with logic. All the logic is put in a json request and this cloud function deals with the logic of the json and returns a json with the desired output, which is an event trigger.a

ps. libraries are imported in the functions instead of conventionally on top, since google cloud functions need them this way
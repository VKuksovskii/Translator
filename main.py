from parse import Parser
from tags import *

print('*** VoiceXML 2.1 to Python 2.7 Translator ***')
print('Input: \'vxml-file path \' \'py-file path\'')
# inputedLine = raw_input('> ')

# paths = inputedLine.split(' ')
paths = ['test.vxml', '1.txt']


def describeTag(three, outfile, ancestor=None, lvl=0):
    for t in three:
        tag = 'tag%s' % lvl
        outfile.write(tag + ' = ' + t[0] + '\n')

        if not (ancestor is None):
            outfile.write(ancestor + '.internalTags.append(' + tag + ')' + '\n')
        lvl += 1
        describeTag(t[1], outfile, tag, lvl)





try:
    three = Parser(paths[0])
    dir(three[0])
    outfile = open(paths[1], 'w')


    outfile.write('import base' + '\n')
    outfile.write('import tags' + '\n')
    outfile.write('\n')

    outfile.write(three[0].describe())

    outfile.close()

    """
            //
    // Initialization Phase
    //

    foreach ( <var>, <script> and form item, in document order )
       if ( the element is a <var> )
         Declare the variable, initializing it to the value of
         the "expr" attribute, if any, or else to undefined.
       else if ( the element is a <script> )
         Evaluate the contents of the script if inlined or else
         from the location specified by the "src" attribute.
       else if ( the element is a form item )
         Create a variable from the "name" attribute, if any, or
         else generate an internal name.  Assign to this variable
         the value of the "expr" attribute, if any, or else undefined.
                foreach ( input item and <initial> element )
                     Declare a prompt counter and set it to 1.

    if ( user entered this form by speaking to its
          grammar while in a different form)
    {
        Enter the main loop below, but start in
        the process phase, not the select phase:
        we already have a collection to process.
    }

    //
    // Main Loop: select next form item and execute it.
    //

    while ( true )
    {
        //
        // Select Phase: choose a form item to visit.
        //

        if ( the last main loop iteration ended
                  with a <goto nextitem> )
            Select that next form item.

        else if (there is a form item with an
                  unsatisfied guard condition )
            Select the first such form item in document order.

        else
            Do an <exit/> -- the form is full and specified no transition.

        //
        // Collect Phase: execute the selected form item.
        //
        // Queue up prompts for the form item.

        unless ( the last loop iteration ended with
                a catch that had no <reprompt>, 
            and the active dialog was not changed )
        {

            Select the appropriate prompts for an input item or <initial>.
            Queue the selected prompts for play prior to
            the next collect operation.

            Increment an input item's or <initial>'s prompt counter.
        }

        // Activate grammars for the form item.

        if ( the form item is modal )
            Set the active grammar set to the form item grammars,
            if any. (Note that some form items, e.g. <block>,
            cannot have any grammars).
        else
            Set the active grammar set to the form item
            grammars and any grammars scoped to the form,
            the current document, and the application root
            document.

        // Execute the form item.

        if ( a <field> was selected )
            Collect an utterance or an event from the user.
        else if ( a <record> was chosen )
            Collect an utterance (with a name/value pair
            for the recorded bytes) or event from the user.
        else if ( an <object> was chosen )
            Execute the object, setting the <object>'s
            form item variable to the returned ECMAScript value.
        else if ( a <subdialog> was chosen )
            Execute the subdialog, setting the <subdialog>'s
            form item variable to the returned ECMAScript value.
        else if ( a <transfer> was chosen )
            Do the transfer, and (if wait is true) set the
            <transfer> form item variable to the returned
            result status indicator.
        else if ( an <initial> was chosen )
            Collect an utterance or an event from the user.
        else if ( a <block> was chosen )
        {
            Set the block's form item variable to a defined value.

            Execute the block's executable context.
        }

        //
        // Process Phase: process the resulting utterance or event.
        //

        Assign the utterance and other information about the last
        recognition to application.lastresult$.
                // Must have an utterance

        if ( the utterance matched a grammar belonging to a <link> )
          If the link specifies an "next" or "expr" attribute,
          transition to that location.  Else if the link specifies an
          "event" or "eventexpr" attribute, generate that event.

        else if ( the utterance matched a grammar belonging to a <choice> )
          If the choice specifies an "next" or "expr" attribute,
          transition to that location.  Else if the choice specifies
          an "event" or "eventexpr" attribute, generate that event.

        else if ( the utterance matched a grammar from outside the current
                  <form> or <menu> )
        {
          Transition to that <form> or <menu>, carrying the utterance
          to the new FIA.
        }

        // Process an utterance spoken to a grammar from this form.
        // First copy utterance result property values into corresponding
        // form item variables.

        Clear all "just_filled" flags.

        if ( the grammar is scoped to the field-level ) {
           // This grammar must be enclosed in an input item.  The input item
           // has an associated ECMAScript variable (referred to here as the input
           // item variable) and slot name.

           if ( the result is not a structure )
             Copy the result into the input item variable.
           elseif ( a top-level property in the result matches the slot name
                    or the slot name is a dot-separated path matching a
                    subproperty in the result )
             Copy the value of that property into the input item variable.
           else
             Copy the entire result into the input item variable

           Set this input item's "just_filled" flag.
        }
        else {
           foreach ( property in the user's utterance )
           {
              if ( the property matches an input item's slot name )
              {
                 Copy the value of that property into the input item's form
                 item variable.

                 Set the input item's "just_filled" flag.
              }
           }
        }


        // Set all <initial> form item variables if any input items are filled.

        if ( any input item variable is set as a result of the user utterance )
            Set all <initial> form item variables to true.

        // Next execute any triggered <filled> actions. 

        foreach ( <filled> action in document order )
        {
            // Determine the input item variables the <filled> applies to.

            N = the <filled>'s "namelist" attribute.

            if ( N equals "" )
            {
               if ( the <filled> is a child of an input item )
                 N = the input item's form item variable name.
               else if ( the <filled> is a child of a form )
                 N = the form item variable names of all the input
                     items in that form.
            }

            // Is the <filled> triggered?

            if ( any input item variable in the set N was "just_filled"
                   AND  (  the <filled> mode is "all"
                               AND all variables in N are filled
                           OR the <filled> mode is "any"
                               AND any variables in N are filled) )
                 Execute the <filled> action.

             If an event is thrown during the execution of a <filled>,
                 event handler selection starts in the scope of the <filled>,
             which could be an input item or the form itself.
        }
        // If no input item is filled, just continue.
    }"""


except IOError:
    print('file not exist')

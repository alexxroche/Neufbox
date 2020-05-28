#!/usr/bin/env perl
# html2ascii.perl: perform preprocessing for spelling checker on an
#                  HTML file: remove the HTML tags and convert the
#                  file to a list of words. 
# usage:           ./html2ascii.perl file
# 980228 erik.tjong@ling.uu.se

# get the name of the file
if (! ($inFile = shift(@ARGV))) { 
   printf STDERR "no input file defined\n";
   exit(1);
}

# open the file
if (! open(INFILE,$inFile)) {
   printf STDERR "file $inFile cannot be opened\n";
   exit(1);
} 

# process the lines of the input file
while (<INFILE>) {
   # give the line a name
   $line = $_;

   # remove HTML tags from line (commands are too general)
   # the s command means substitute. It replaces the first pattern
   # between slashes with the second pattern. Here the first pattern
   # will be deleted because the second pattern is empty. In the first
   # pattern we see the sequence [^>]* which stands for a sequence of
   # characters that are not equal to >. In the patterns < and > stand
   # for themselves while ^ means start-of-line and $ end-of-line 
   $line =~ s/<[^>]*>//g;    # remove complete html tags
   $line =~ s/<[^>]*$//g;    # remove starts of html tags
   $line =~ s/^[^>]*>//g;    # remove ends of html tags

   # replace SGML entities for the Swedish vowels to ISO Latin 1
   $line =~ s/&aring;/å/g;   
   $line =~ s/&auml;/ä/g;   
   $line =~ s/&ouml;/ö/g;   
   $line =~ s/&Aring;/Å/g;   
   $line =~ s/&Auml;/Ä/g;   
   $line =~ s/&Ouml;/Ö/g;   

   # convert every white space character (\s) to a newline (\n): this
   # will get every word on a seperate line and thus convert the file
   # to a word list 
   $line =~ s/\s/\n/g;

   # get rid of some punctuation marks
   # we will assume that they can be found behind the words: this
   # requires two instructions because in the Perl string some words
   # will stand before a new line character (\n) while the last word
   # might stand before the end-of-line character ($).
   $line =~ s/[\.?,:;!]$//g;
   $line =~ s/[\.?,:;!]\n/\n/g;

   # get rid of quote signs; the ' sign could be part of a genitive
   # construction so we will only remove it when it stands in front of
   # or after a word
   $line =~ s/["`]//g;
   $line =~ s/'$//g;
   $line =~ s/'\n/\n/g;
   $line =~ s/^'//g;
   $line =~ s/\n'/\n/g;

   # we are done (hopefully)
   # print the line
   printf $line;
}
# end of program
exit(0);


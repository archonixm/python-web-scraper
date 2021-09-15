import re
import nltk
from nltk import ngrams
from difflib import get_close_matches as gcm


# Extract skills from text
# Change threshold for string matching, the higher the threshold the stricter is the matching
def extract_skills(info, skills, threshold=0.9):
    # Convert text to unigrams, bigrams and trigrams
    words, unigrams, bigrams, trigrams = clean_info(info)
    results = []
    # Iterate through all the skills
    for skill in skills:
        s = skill
        # If a skill has a abbreviation e.g. Amazon Web Service (AWS)
        # We match the abbreviation directly first
        if '(' in s:
            abb = s[s.find("(")+1:s.find(")")]
            if abb in words:
                results.append(skill)
                continue
            s = re.sub(r"[\(].*?[\)]", "", s)
        s = s.lower()
        s2 = s.split()
        if len(s2) > 1:
            # If skill can be found directly in the text
            if s in info.lower():
                results.append(skill)
                continue
        # Skill consist of one word
        if len(s2) == 1:
            if len(gcm(s, unigrams, cutoff=threshold)) > 0:
                results.append(skill)
        # Skill consist of two words
        elif len(s2) == 2:
            if len(gcm(s, bigrams, cutoff=threshold)) > 0:
                results.append(skill)
        # Skill consist of three words
        elif len(s2) == 3:
            if len(gcm(s, trigrams, cutoff=threshold)) > 0:
                results.append(skill)
        else:
            if len(gcm(s, trigrams, cutoff=threshold)) > 0:
                results.append(skill)
    return results

# Remove the skills to ignore from the extracted skill list
# And for duplicate skills, replace them with the original skill name
def extract_ignore(skills, redundant_skills, duplicate_skills):
    ignore_skills = []
    for j, skill in enumerate(skills):
        if skill in redundant_skills:
            ignore_skills.append(skill)
            continue
        for other in skills[:j] + skills[j+1:]:
            try:
                if skill in other:
                    if find_whole_word(skill, other):
                        ignore_skills.append(skill)
                        break
            except:
                pass
    job_skills = []
    for skill in skills:
        if skill not in ignore_skills:
            if skill in duplicate_skills.keys():
                skill = duplicate_skills[skill]
            job_skills.append(skill)
    return list(set(job_skills)), list(set(ignore_skills))

# Text cleaning
def clean_info(info):
    # Remove ordered list with alphabets: a), b), c),...
    words = re.sub(r'[\s\t\n|.|\(]+[a-zA-Z\s*][.|\)]+', ' ', info)
    # Remove non-ASCII characters
    words = re.sub(r'[^\x00-\x7F]+', ' ', words)
    # Remove punctuations
    words = re.sub('[\n|,|.|:|;|\-|/|\(|\)|\[|\]]', ' ', words)
    # Convert text to unigrams, bigrams and trigrams
    unigrams = [word.strip() for word in words.lower().split()]
    bigrams = [' '.join(g) for g in ngrams(unigrams, 2)]
    trigrams = [' '.join(g) for g in ngrams(unigrams, 3)]
    return words.split(), unigrams, bigrams, trigrams

# Check if the search_string is in input_string as a word (it is between two white spaces) 
def find_whole_word(search_string, input_string):
    raw_search_string = r"\b" + search_string + r"\b"
    match_output = re.search(raw_search_string, input_string)
    no_match_was_found = ( match_output is None )
    if no_match_was_found:
        return False
    else:
        return True

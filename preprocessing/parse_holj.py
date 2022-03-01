import argparse
import collections
import os
import glob
import json
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(
    description='Extract HOLJ examples into jsonl format.')
parser.add_argument('-i',
                    '--input_dir',
                    type=str,
                    help='Input directory containing xml files.')
parser.add_argument('-o',
                    '--output_dir',
                    default="./",
                    type=str,
                    help='Directory where jsonl files will be written')

Sentence = collections.namedtuple('Sentence', "tokens sid label".split())


def splitallext(filename):
  main, ext = os.path.splitext(os.path.basename(filename))
  if ext:
    return splitallext(main)
  else:
    return main


def add_text_from_node(sent_tokens, node):
  if node.tag == 'W':
    if node.text is not None:
      sent_tokens.append(node.text)
    else:
      for w in node.findall('W'):
        add_text_from_node(sent_tokens, w)

def main():

  args = parser.parse_args()

  for filename in glob.glob(args.input_dir + "/*"):

    body, = ET.parse(filename).getroot().findall('BODY')
    lord_sentences = {}

    for i, lord_node in enumerate(body.findall('LORD')):
      lord_sentences[i] = []
      for p_node in lord_node.findall('P'):
        for sent_node in p_node.findall('SENT'):
          sent_tokens = []
          for child in sent_node:
            add_text_from_node(sent_tokens, child)
          if 'TYPE' not in sent_node.attrib:
            sent_type = 'NONE'
          else:
            sent_type = sent_node.attrib['TYPE']
          lord_sentences[i].append(
              Sentence(sent_tokens, sent_node.attrib["sid"], sent_type))

    minimal_file_name = splitallext(filename)

    with open(args.output_dir + minimal_file_name + ".jsonl", 'w') as f:
      for index, sentences in lord_sentences.items():
        f.write(
            json.dumps({
                "doc_id": minimal_file_name + "_" + str(index),
                "labels": [s.label for s in sentences],
                "sentences": [" ".join(s.tokens) for s in sentences],
                "tokenized_sentences": [s.tokens for s in sentences]
            }) + "\n")


if __name__ == "__main__":
  main()

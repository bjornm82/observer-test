import numpy as np
import csv

from typing import List, Optional, Dict, Union, Iterator, Iterable
import collections
from dataclasses import dataclass
import pprint

import pandas as pd

from presidio_analyzer import AnalyzerEngine, RecognizerResult

from pandas_profiling import ProfileReport

csv_file = "username-password-recovery-code.csv"

df = pd.read_csv(csv_file,
    sep=';',
    skipinitialspace = True,
    quotechar = '"',
    encoding= 'unicode_escape')

profile = ProfileReport(df, title="Pandas Profiling Report", explorative=True)

profile.to_file("your_report.html")

json_data = profile.to_json()

profile.to_file("your_report.json")


df_dict = df.to_dict(orient="list")


@dataclass
class DictAnalyzerResult:
    """Hold the analyzer results per value or list of values."""
    key: str
    value: Union[str, List[str]]
    recognizer_results: Union[List[RecognizerResult], List[List[RecognizerResult]]]


class BatchAnalyzerEngine(AnalyzerEngine):
    """
    Class inheriting from AnalyzerEngine and adds the funtionality to analyze lists or dictionaries.
    """
    
    def analyze_list(self, list_of_texts: Iterable[str], **kwargs) -> List[List[RecognizerResult]]:
        """
        Analyze an iterable of strings
        
        :param list_of_texts: An iterable containing strings to be analyzed.
        :param kwargs: Additional parameters for the `AnalyzerEngine.analyze` method.
        """
        
        list_results = []
        for text in list_of_texts:
            results = self.analyze(text=text, **kwargs) if isinstance(text, str) else []
            list_results.append(results)
        return list_results

    def analyze_dict(
     self, input_dict: Dict[str, Union[object, Iterable[object]]], **kwargs) -> Iterator[DictAnalyzerResult]:
        """
        Analyze a dictionary of keys (strings) and values (either object or Iterable[object]). 
        Non-string values are returned as is.
        
        :param input_dict: The input dictionary for analysis
        :param kwargs: Additional keyword arguments for the `AnalyzerEngine.analyze` method
        """
        
        for key, value in input_dict.items():
            if not value:
                results = []
            else:
                if isinstance(value, str):
                    results: List[RecognizerResult] = self.analyze(text=value, **kwargs)
                elif isinstance(value, collections.abc.Iterable):
                    results: List[List[RecognizerResult]] = self.analyze_list(
                                list_of_texts=value, 
                                **kwargs)
                else:
                    results = []
            yield DictAnalyzerResult(key=key, value=value, recognizer_results=results)



pprint.pprint(df_dict)
batch_analyzer = BatchAnalyzerEngine()
analyzer_results = batch_analyzer.analyze_dict(df_dict, language="en")

results = pd.DataFrame(analyzer_results)
pprint.pprint(results)

# Segment error therefor default_handler = str
result = results.to_json(orient='records', default_handler = str)

text_file = open("analysed_report.json", "w")
text_file.write(result)
text_file.close()
# pymarkertools
Marker tools for working with Aruco and April Tag markers. 
Currently only contains one, but it's a start :-)

## Generate Marker PDF
This allows to customize different Markers for printout 
- mm exact configuration of marker size for printout
- mm exact configuration of distance between markers in x and y
- marker labeling with marker id and configurable text
- draws cutmarks for each marker
- generates multi-page PDF for easy printing when generating large amount of markers

How to use  
- see Pipfile for needed packages
- Run the generate_marker_pdf.py example and look for the pdf generated. 
- Change the settings in the init to adjust to your needs

## License 
  Copyright 2019 Marco Noll, Garmin International Inc.
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0
  
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

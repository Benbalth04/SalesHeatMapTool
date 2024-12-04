### Begin testing seperate python files, and get it to work like current map generator file

- Create seperate python scripts for:
    1) Reading sales data (just one big file)
    2) Parsing geoson data
    3) Combining and returning the map
- Add more customization ability for generating map (e.g. what color maps, any marker locations ?, search bar, legends, expand)
    - Goal is to make map generation more modular
    - Add address api for marker locations or handle for coordinates

- change years dropdown to just be a calender start and end date selector (then just hard code to round to years for now)
- Move over to leaflet to allow for clicking event handlers on choropleths 
- Handle for international resolution
- Setup firebase authentification
- Setup firebase database 
    - User color, location preferences 
    - Saved markers
- Once map is generated, hide all options dropdowns and change the generate map button to be a reset button, which restores main.html to its original state, and deletes anything in the public/maps folder
- download state and national shapefiles 
    - Update python script to handle appropriately (front-end alreay configured)
- change years dropdown to just be a calender start and end date selector (then just hard code to round to years for now)
- Create seperate python scripts for:
    1) Reading sales data (just one big file)
    2) Parsing geoson data
    3) Combining and returning the map
- Move over to leaflet to allow for clicking event handlers on choropleths 
- Setup firebase authentification
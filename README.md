# Luo video tuloksista ja heittäjistä

Tämä python scripti luo kaksi tiedostoa: Yhden pelaajista ja toisen pelitilanteesta:

Miten ajaa:
- Hae pelin id https://pinq.kapsi.fi sivulta. (avaa haluamasi peli ja katso mistä apista tiedot haetaan)
	Osotie on muotoa: https://pinq.kapsi.fi/DK/api/data/game/********
	loppu osuus on pelin id
- korvaa tiedostosta muuttuja 'game_id' uudella id:llä
- aja scripti
- leikkaa heitot duartion ajan pituisiksi (tässä tapauksessa 7s (results = 5 + 2)), niin kaikki asettuu itsestään paikoilleen
- profit

Huomiota:
- Luo tiedostot sinne missä python scriptikin on
- Tiedostojen nimet "names_*****" ja "results_******"
- duration muuttuja kertoo kuinka monta sekunttia ensimmäistä kuvaa toistetaan ja kuinka monta sekunttia toista kuvaa toistetaan. Tämä siksi että edellinen heitto ei olisi kokoajan näkyvillä ja hämmentämässä. 
- "Koti_aloittaa" määrittää kumpi aloittaa eka. 



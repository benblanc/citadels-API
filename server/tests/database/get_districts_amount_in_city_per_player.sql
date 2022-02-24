SELECT 
    player_uuid, SUM(amount) AS buildings_in_city
FROM
    citadels.buildings
GROUP BY player_uuid ASC;

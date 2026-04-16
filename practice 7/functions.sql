CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT phonebook.name, phonebook.phone
    FROM phonebook
    WHERE phonebook.name ILIKE '%' || pattern || '%'
       OR phonebook.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_contacts_paginated(lim INT, off INT)
RETURNS TABLE(name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT phonebook.name, phonebook.phone
    FROM phonebook
    ORDER BY phonebook.id
    LIMIT lim OFFSET off;
END;
$$ LANGUAGE plpgsql;
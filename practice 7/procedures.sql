
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;



CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = p_value OR phone = p_value;
END;
$$;



CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    names TEXT[],
    phones TEXT[],
    OUT invalid_data TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    invalid_data := ARRAY[]::TEXT[];

    FOR i IN 1..array_length(names, 1) LOOP

       
        IF phones[i] ~ '^[0-9]{11}$' THEN

            IF EXISTS (SELECT 1 FROM phonebook WHERE name = names[i]) THEN
                UPDATE phonebook
                SET phone = phones[i]
                WHERE name = names[i];
            ELSE
                INSERT INTO phonebook(name, phone)
                VALUES (names[i], phones[i]);
            END IF;

        ELSE
            invalid_data := array_append(invalid_data, names[i] || ':' || phones[i]);
        END IF;

    END LOOP;
END;
$$;
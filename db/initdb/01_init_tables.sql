create table users (
    uuid text primary key not null,
    delta int not null,
    area text not null,
    created_at timestamp with time zone not null default NOW(),
    updated_at timestamp with time zone not null default NOW()
);

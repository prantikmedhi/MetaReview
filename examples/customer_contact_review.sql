select
  customer_id,
  customer_full_name,
  email,
  phone_number,
  ssn,
  credit_card
from acme_nexus_raw_data.acme_raw.crm.customers
where email is not null
  and phone_number is not null;

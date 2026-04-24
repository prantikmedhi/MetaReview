select
  customer_id,
  email,
  phone_number,
  ssn,
  credit_card_number
from acme_nexus_raw_data.acme_raw.crm.customers
where email is not null;

# Testing

<span style="color:red"> Those tests aren't finished yet </span>

Here are commands and expected result files :

1. Default, filter nothing

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/default.json
    ```

2. Test country filter, Keep Luxembourg records only

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/country.json -cf LU
    ```

3. Filter AS numbers, POST Luxembourg

    <span style="color:red"> ASN Filter not working yet. </span>

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/asn -pf -cl 6661 --match more
    ```

4. Prefix filter, keep records that 38.126.253.0/24 or 59.90.188.0/24 will match exactly

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/cidr_exact.json -pf -cl 38.126.253.0/24 59.90.188.0/24 --match exact
    ```

5. Keep records that prefix are contained by 38.126.0.0/16

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/cidr_more.json -pf -cl 38.126.0.0/16 --match more
    ```

6. Keep ipv4 records

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/ipversion.json --ipversion 4
    ```

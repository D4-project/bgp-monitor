# Testing

Here are commands and expected result files :

1. Default, filter nothing

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/default.json
    ```

2. Test country filter, Restrict the result to Luxembourg records only

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/country.json -cf LU
    ```

3. Filter by AS numbers, Restrict the result to elements that AS path contains 268696 or 3356.

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/asn.json -af 268696 3356
    ```

4. Negative filtering on AS Number, Restrict the result to elements that AS path do not contains 3356, 17794 or 265636

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/asn_neg.json -af _3356 _17794 _265636
    ```

5. Prefix filter, Restrict the result to only elements with an IP prefix that exactly match to 38.126.253.0/24 or 59.90.188.0/24

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/cidr_exact.json -pf -cl 38.126.253.0/24 59.90.188.0/24 --match exact
    ```

6. Restrict the result to only elements with an IP prefix contained by 38.126.0.0/16

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/cidr_more.json -pf -cl 38.126.0.0/16 --match more
    ```

7. Restrict the result to only elements with prefixes belonging to the given IP address version

    ```shell
    python3 feeder.py --noail --input_data ../datasets/test1 --input_record_type upd -jo ../datasets/results/ipversion.json --ipversion 4
    ```

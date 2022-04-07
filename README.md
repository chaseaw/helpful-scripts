Helpful Scripts
================================================================================
Plainly, this is the intended repository for short scripts that are useful but not an integral part of other programs.

List of scripts
--------------------------------------------------------------------------------
* [Index_Caller.py](Index_Caller.py)
  * Dependencies: Base Python (2 or 3 should work)
  * Input: Index read fastqs from a MiSeq
  * Output: .csv with most frequently occuring barcodes
  * Useful for: figuring whether barcodes were misassigned

* [new-barcodes.py](Index_Caller.py)
  * Dependencies: Base Python (2 or 3 should work, definitely runs on 3.9.5)
  * Input: A single column .csv file containing a list of same-length barcodes (e.g. 8 for MiSeq)
  * Output: barcode_nt_distributions.csv, barcode_distances.csv (hamming), and new_barcodes.csv
  * Useful for: creating new unique barcodes to assign to new users

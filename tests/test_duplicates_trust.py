# duplicates on the real 26 Sept data - no shared hash can be trusted
import unittest
from collections import Counter
from agent.skills import duplicates
from helpers import build_runtime

INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming

# each Incoming original has a 880 byte copy with the same name, sizes in the comments
PO_ID = "732439a0-7f36-4d31-ac3b-f406c41c00bd"  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)
PO_COPY_ID = "3dd05bfb-f423-44bb-ad0f-fc94acca3ced"  # PO_4471_ApexMetals_signed.pdf (880 bytes)
PO_1_ID = "82f83d94-5a46-4df3-9ee1-61e8b3c79d6e"  # PO_4471_ApexMetals_signed (1).pdf (218,044 bytes)
PO_1_COPY_ID = "c0c8b9c0-85c2-4528-b574-1f35665616b6"  # PO_4471_ApexMetals_signed (1).pdf (880 bytes)

SHARED_HASH_COUNT = 14  # hashes shared by 2+ files on 26 Sept
INCOMING_FILE_COUNT = 18
SUSPECTED = "name + size (suspected)"


def _all_files():
    # every file row on a fresh fake server with the 26 Sept data
    rt, _ = build_runtime("plan")
    return rt.ctx.files()


class SharedHashTests(unittest.TestCase):  # DUP-3

    def test_shared_hashes_untrusted(self):
        # all 14 shared hashes untrusted on 26 Sept data, incl the hash on every Incoming file
        files = _all_files()
        hash_counts = Counter(f["content_hash"] for f in files if f.get("content_hash"))
        shared_hashes = {h for h, count in hash_counts.items() if count > 1}
        untrusted = duplicates.untrustworthy_hashes(files)
        self.assertEqual(len(untrusted), SHARED_HASH_COUNT)
        self.assertEqual(untrusted, shared_hashes)
        incoming = [f for f in files if f.get("folder_id") == INCOMING_FOLDER_ID]
        self.assertEqual(len(incoming), INCOMING_FILE_COUNT)
        trusted_in_incoming = [f["filename"] for f in incoming if f.get("content_hash") not in untrusted]
        self.assertEqual(trusted_in_incoming, [])

    def test_po_pairs_suspected(self):
        # the 2 PO pairs are the only duplicate groups and both only suspected
        files = _all_files()
        groups = duplicates.find_groups(files)
        self.assertEqual(len(groups), 2)
        # groups come back in server order so compare as a set
        found = {(g.original["id"], tuple(c["id"] for c in g.copies), g.basis) for g in groups}
        self.assertEqual(found, {
            (PO_ID, (PO_1_ID,), SUSPECTED),
            (PO_COPY_ID, (PO_1_COPY_ID,), SUSPECTED),
        })


if __name__ == "__main__":
    unittest.main()

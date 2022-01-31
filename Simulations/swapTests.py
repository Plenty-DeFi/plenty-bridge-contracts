import smartpy as sp

FA2_TOKEN = sp.io.import_script_from_url("file:./Tokens/FA2_multi_minter.py")

SWAP = sp.io.import_script_from_url("file:./Swap/swap.py")

def global_parameter(env_var, default):
    try:
        if os.environ[env_var] == "true" :
            return True
        if os.environ[env_var] == "false" :
            return False
        return default
    except:
        return default

if "templates" not in __name__:
    @sp.add_test(name = "SwapTests")
    def test():
        admin = sp.test_account("Admin")
        alice = sp.test_account("Alice")
        bob = sp.test_account("Bob")
        cat = sp.test_account("Cat")
        minter1 = sp.test_account("Minter1")
        minter2 = sp.test_account("Minter2")
        
        config = FA2_TOKEN.FA2_config(
                debug_mode = global_parameter("debug_mode", False),
                single_asset = global_parameter("single_asset", False),
                non_fungible = global_parameter("non_fungible", False),
                add_mutez_transfer = global_parameter("add_mutez_transfer", False),
                readable = global_parameter("readable", True),
                force_layouts = global_parameter("force_layouts", True),
                support_operator = global_parameter("support_operator", True),
                assume_consecutive_token_ids =
                    global_parameter("assume_consecutive_token_ids", True),
                store_total_supply = global_parameter("store_total_supply", False),
                lazy_entry_points = global_parameter("lazy_entry_points", False),
                allow_self_transfer = global_parameter("allow_self_transfer", False),
                use_token_metadata_offchain_view = global_parameter("use_token_metadata_offchain_view", True),
            )
        scenario = sp.test_scenario()

        scenario.h1("Initializing swap")
        c1 = SWAP.Swap(_oldTokenAddress = alice.address, _newTokenAddress = alice.address, admin = admin.address)

        scenario += c1

        scenario.h1("Creating old token")
        oldToken = FA2_TOKEN.FA2(config = config,
                 metadata = sp.utils.metadata_of_url("https://example.com"),
                 admin = admin.address,
                 minter1 = minter1.address,
                 minter2 = minter2.address)
        scenario += oldToken

        scenario.h1("Creating new token")
        newToken = FA2_TOKEN.FA2(config = config,
                 metadata = sp.utils.metadata_of_url("https://example.com"),
                 admin = admin.address,
                 minter1 = minter1.address,
                 minter2 = c1.address)
        scenario += newToken
        
        scenario.h1("Setting addresses")
        c1.setAddress(sp.record(oldTokenAddress = oldToken.address, newTokenAddress = newToken.address)).run(sender = admin)

        scenario.h1("Minting/Creating old token id = 0")
        oldTok1_md = FA2_TOKEN.FA2.make_metadata(
            name = "wUSDT",
            decimals = 6,
            symbol= "wUSDT")
        oldToken.mint(address = bob.address,
                            amount = 100,
                            metadata = oldTok1_md,
                            token_id = 0).run(sender = minter1)

        scenario.h1("Minting/Creating new token id = 0")
        newTok1_md = FA2_TOKEN.FA2.make_metadata(
            name = "USDT.e",
            decimals = 6,
            symbol= "USDT.e")
        newToken.mint(address = admin.address,
                            amount = 100,
                            metadata = newTok1_md,
                            token_id = 0).run(sender = minter1)

        scenario.h1("Setting Swap as opreator for bob's old token")
        oldToken.update_operators([
                sp.variant("add_operator", oldToken.operator_param.make(
                    owner = bob.address,
                    operator = c1.address,
                    token_id = 0
                ))
            ]).run(sender = bob, valid = True)

        scenario.h1("Swapping old token for new one")
        c1.swapTokens(sp.record(tokenId = 0, amount = 50)).run(sender = bob)

        scenario.h1("Swapping old token for new one")
        c1.swapTokens(sp.record(tokenId = 0, amount = 50)).run(sender = bob)

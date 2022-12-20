let web3 = new Web3(Web3.givenProvider || "https://rpc.sepolia.dev");
console.log("cookie")
console.log(document.cookie)
web3.eth.defaultAccount = "0x3F841f06A5e6CeF72450cE1303b25CBC76A97Ed1";
const test_address = "0x9f27f5791D5031cA89d0CA6D59276659EAD06242"
const test_abi = [
	{
		"inputs": [],
		"name": "add",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	}
];

const test_contract = new web3.eth.Contract(test_abi, test_address);

async function start() {
    var added_val = await test_contract.methods.add().call({from:web3.eth.defaultAccount});
    console.log(added_val);
}


start();

web3.eth.getBalance(web3.eth.defaultAccount).then((response) => {
    $("#csx-token").html(response);
});


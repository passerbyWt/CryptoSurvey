
var f=function (){
    
	let web3 = new Web3(Web3.givenProvider || "https://rpc.sepolia.dev");

    let privateKey = document.getElementById("private_key").value;
    // let publicKey = web3.utils.keccak256(privateKey);
    // let addr ="0x"+ publicKey.toString('hex');
    document.cookie='tired'
    // document.cookie="address="+privateKey;
    window.location.href=["dashboard.html"];
    // console.log(addr)
}


document.getElementById("submit_0").onclick= f;
